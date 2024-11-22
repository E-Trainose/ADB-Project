import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import joblib

# Define the neural network class (same as in training)
class TunedSensorClassifier(nn.Module):
    def __init__(self, input_size, num_classes):
        super(TunedSensorClassifier, self).__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, num_classes)
        self.dropout = nn.Dropout(0.3)
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

# Load the saved model and label encoder
model_path = '/home/orin/Documents/nn_model.pth'
label_encoder_path = '/home/orin/Documents/label_encoder_nn.pkl'

label_encoder = joblib.load(label_encoder_path)
num_classes = len(label_encoder.classes_)
input_size = None  # Update this after loading data

model = None

# Load new data for testing
file_path = '/home/orin/Downloads/test_dataset.csv'
data = pd.read_csv(file_path)

# Ensure the feature columns align with the trained model
X_new = data.drop(columns=['LABEL']) if 'LABEL' in data.columns else data
input_size = X_new.shape[1]  # Update input size based on data

# Initialize the model with correct dimensions
model = TunedSensorClassifier(input_size, num_classes)
model.load_state_dict(torch.load(model_path))
model.eval()

# Convert the new data into PyTorch tensors
X_new_tensor = torch.tensor(X_new.values, dtype=torch.float32)

# Perform predictions
with torch.no_grad():
    outputs = model(X_new_tensor)
    _, predicted_classes = torch.max(outputs.data, 1)

# Decode the predicted class indices to original labels
predicted_labels = label_encoder.inverse_transform(predicted_classes.numpy())

# Append predictions to the dataset
data['PREDICTED_LABEL'] = predicted_labels

# Save the predictions to a new file
output_file = '/home/orin/Documents/prediction_result.csv'
data.to_csv(output_file, index=False)

print(f"Predictions saved to '{output_file}'")
