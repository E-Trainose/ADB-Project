from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib
import torch
import torch.nn as nn
from scipy.stats import skew, kurtosis
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

class AiStarter:
    def __init__(self):
        pass

class BaseClassifier:
    def predict(self, datas : pd.DataFrame):
        raise NotImplementedError()
    def train(self, datas : pd.DataFrame):
        raise NotImplementedError()
    def save(self, path : str):
        raise NotImplementedError()

class BasePreproccessor:
    def preproccess(self, datas):
        raise NotImplementedError()
    
class DefaultPreprocessor(BasePreproccessor):
    def __init__(self):
        super().__init__()

    def preproccess(self, datas):
        # Function to extract features
        def __extractFeatures(data_chunk, sensor):
            return {
                f'MEAN_{sensor}': data_chunk[sensor].mean(),
                f'MIN_{sensor}': data_chunk[sensor].min(),
                f'MAX_{sensor}': data_chunk[sensor].max(),
                f'SKEW_{sensor}': skew(data_chunk[sensor]),
                f'KURT_{sensor}': kurtosis(data_chunk[sensor])
            }

        sensor_columns = ['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8','TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3']
        
        processed_data = pd.DataFrame()

        # Split data into chunks of 156 rows
        num_chunks = len(datas) // 156

        for i in range(num_chunks):
            data_chunk = datas.iloc[i * 156:(i + 1) * 156]
            features = {}

            # Extract features for each sensor
            for sensor in sensor_columns:
                features.update(__extractFeatures(data_chunk, sensor))

            dfeatures = pd.DataFrame(features, index=[0])

            # Append to the final DataFrame
            processed_data = pd.concat([dfeatures, processed_data])

        return processed_data
    
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

        self.preprocessor = DefaultPreprocessor()

    def load(self, model_path, label_encoder_path):
        # Load the saved model and label encoder
        self.model_path = model_path
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        data = self.preprocessor.preproccess(data)
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

        self.preprocessor = DefaultPreprocessor()

    def load(self, model_path, label_encoder_path):
        self.svm_model = joblib.load(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        data = self.preprocessor.preproccess(data)
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

        self.preprocessor = DefaultPreprocessor()

    def load(self, model_path, label_encoder_path):
        self.rf_model=joblib.load(model_path)
        self.label_encoder = joblib.load(label_encoder_path)

    def predict(self, data):
        data = self.preprocessor.preproccess(data)
        X_new = data.drop(columns=['LABEL']) if 'LABEL' in data.columns else data
        predicted_classes = self.rf_model.predict(X_new)
        predicted_labels = self.label_encoder.inverse_transform(predicted_classes)

        return predicted_labels
    

class PredictionThread(QThread):
    finished = pyqtSignal(np.ndarray)

    def setAIModel(self, model : BaseClassifier):
        self.model = model

    def setDatas(self, datas : pd.DataFrame):
        self.datas = datas

    def run(self):
        try:
            predictions = self.model.predict(self.datas)
            predictions = np.array(predictions)
            print(predictions)
        
        except Exception as e:
            print(f"Error during prediction: {e}")

        finally:
            self.finished.emit(predictions)