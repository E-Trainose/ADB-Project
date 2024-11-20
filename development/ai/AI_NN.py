import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# Load and preprocess data
file_path = '/home/orin/Downloads/Processed_Sensor_Data.csv'
data = pd.read_csv(file_path)

X = data.drop(columns=['LABEL'])
y = data['LABEL']

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.long)
y_test_tensor = torch.tensor(y_test, dtype=torch.long)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)  # Tuning batch size
test_loader = DataLoader(test_dataset, batch_size=64, shuffle=False)

# Define a more complex neural network
class TunedSensorClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(TunedSensorClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.3)  # Tuning dropout rate
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.dropout(x)
        x = self.fc4(x)
        return x

# Initialize model, criterion, and optimizer with a tuned learning rate
input_size = X_train.shape[1]
num_classes = len(label_encoder.classes_)
model = TunedSensorClassifier(input_size, num_classes)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0005)  # Lower learning rate

# Training loop
num_epochs = 50  # Higher epoch count
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
    
    # Validation
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    print(f'Epoch [{epoch+1}/{num_epochs}], Loss: {running_loss/len(train_loader):.4f}, Accuracy: {accuracy:.2f}%')

# Final test accuracy
accuracy = 100 * correct / total
print(f'Final Test Accuracy: {accuracy:.2f}%')

# Save the trained model and label encoder
torch.save(model.state_dict(), '/home/orin/Documents/nn_model.pth')
joblib.dump(label_encoder, '/home/orin/Documents/label_encoder_nn.pkl')
print("Model saved as 'nn_model.pth' and label encoder as 'label_encoder_nn.pkl'")
