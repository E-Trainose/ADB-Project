from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib
import torch
import torch.nn as nn



class AiStarter:
    def __init__(self):
        pass

class BaseClassifier:
    def __init__(self):
        pass

    def predict(self, datas : pd.DataFrame):
        pass

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

class NNClassifier(BaseClassifier):
    def __init__(self):
        super(NNClassifier, self).__init__()
        self.model = None
        self.model_path = None
        self.label_encoder = None

    def load(self, model_path, label_encoder_path):
        # Load the saved model and label encoder
        self.model_path = model_path
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        # Ensure the feature columns align with the trained model
        X_new = data.drop(columns=['LABEL']) if 'LABEL' in data.columns else data

        # Convert the new data into PyTorch tensors
        X_new_tensor = torch.tensor(X_new.values, dtype=torch.float32)

        input_size = X_new.shape[1]  # Update input size based on data

        num_classes = len(self.label_encoder.classes_)

        # Initialize the model with correct dimensions
        model = TunedSensorClassifier(input_size, num_classes)
        model.load_state_dict(torch.load(self.model_path))
        model.eval()

        # Perform predictions
        with torch.no_grad():
            outputs = model(X_new_tensor)
            _, predicted_classes = torch.max(outputs.data, 1)

        # Decode the predicted class indices to original labels
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes.numpy())

        return predicted_labels

class SVMClassifier(BaseClassifier):
    def __init__(self):
        super(SVMClassifier, self).__init__()
        self.svm_model = None
        self.label_encoder = None

    def load(self, model_path, label_encoder_path):
        self.svm_model = joblib.load(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        # Ensure the feature columns align with the trained model
        X_new = data.drop(columns=['LABEL']) if 'LABEL' in data.columns else data

        # Perform predictions
        predicted_classes = self.svm_model.predict(X_new)

        # Decode the predicted class indices to original labels
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes)


        return predicted_labels

class RFClassifier(BaseClassifier):
    def __init__(self):
        super(RFClassifier, self).__init__()
        self.rf_model = None
        self.label_encoder = None

    def load(self, model_path, label_encoder_path):
        self.rf_model=joblib.load(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        X_new = data.drop(columns=['LABEL']) if 'LABEL' in data.columns else data
        predicted_classes = self.rf_model.predict(X_new)
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes)

        return predicted_labels



