import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Subset
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import joblib

# Load the processed data
file_path = '/mnt/data/Processed_Sensor_Data.csv'
data = pd.read_csv(file_path)

# Split features and label
X = data.drop(columns=['LABEL'])
y = data['LABEL']

# Encode the labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Convert to PyTorch tensors
X_tensor = torch.tensor(X.values, dtype=torch.float32)
y_tensor = torch.tensor(y_encoded, dtype=torch.long)

# Define k-fold cross-validation
k_folds = 5
kf = KFold(n_splits=k_folds, shuffle=True, random_state=42)

# Define the neural network model with additional layers and batch normalization
class ImprovedSensorClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(ImprovedSensorClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.bn1 = nn.BatchNorm1d(256)
        self.fc2 = nn.Linear(256, 128)
        self.bn2 = nn.BatchNorm1d(128)
        self.fc3 = nn.Linear(128, 64)
        self.bn3 = nn.BatchNorm1d(64)
        self.fc4 = nn.Linear(64, num_classes)
        
        self.dropout = nn.Dropout(0.3)
        self.relu = nn.ReLU()
        
    def forward(self, x):
        x = self.relu(self.bn1(self.fc1(x)))
        x = self.dropout(x)
        x = self.relu(self.bn2(self.fc2(x)))
        x = self.dropout(x)
        x = self.relu(self.bn3(self.fc3(x)))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

# Initialize parameters
input_size = X.shape[1]                    # Number of features
num_classes = len(label_encoder.classes_)   # Number of classes
num_epochs = 50                             # Number of epochs per fold
batch_size = 32
learning_rate = 0.001

# Store the results of each fold
fold_accuracies = []

# Begin k-fold cross-validation
for fold, (train_index, val_index) in enumerate(kf.split(X_tensor)):
    print(f'Fold {fold+1}/{k_folds}')
    
    # Split data for this fold
    X_train, X_val = X_tensor[train_index], X_tensor[val_index]
    y_train, y_val = y_tensor[train_index], y_tensor[val_index]
    
    # Create DataLoaders for the current fold
    train_dataset = TensorDataset(X_train, y_train)
    val_dataset = TensorDataset(X_val, y_val)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize the model, loss function, and optimizer for each fold
    model = ImprovedSensorClassifier(input_size, num_classes)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=15, gamma=0.5)
    
    # Training loop for the current fold
    for epoch in range(num_epochs):
        model.train()
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        # Validation phase for the current fold
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                outputs = model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        accuracy = 100 * correct / total
        print(f'Fold [{fold+1}], Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%')
        
        # Adjust the learning rate
        scheduler.step()
    
    # Store fold accuracy
    fold_accuracies.append(accuracy)

# Print average accuracy across all folds
average_accuracy = np.mean(fold_accuracies)
print(f'Average Accuracy across {k_folds} folds: {average_accuracy:.2f}%')

# Save the model from the last fold
model_save_path = '/mnt/data/improved_sensor_classifier_model.pth'
torch.save(model.state_dict(), model_save_path)

# Save the label encoder
encoder_save_path = '/mnt/data/sensor_label_encoder.pkl'
joblib.dump(label_encoder, encoder_save_path)

model_save_path, encoder_save_path
