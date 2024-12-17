import config
import os
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
import pandas as pd
import joblib


class Classifier:
    def __init__(self):
        print("TEST" + config.WORKING_DIR_PATH)

    def predict(self, datas):
        return [1]
    
    # def train(self, data):
    #     return 1.0
    
    def save(self, folderPath):
        print("Model saved as 'svm_model.pkl' and label encoder as 'label_encoder_svm.pkl'")

    def load(self):
        print("load model")

    def train(self, data : pd.DataFrame):
        # Split features and label
        X = data.drop(columns=['LABEL'])
        y = data['LABEL']

        # Encode the labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)

        # Define the SVM model with a pipeline to standardize the data
        self.svm_model = make_pipeline(StandardScaler(), SVC(kernel='linear', probability=True))

        # Train the SVM model on the full dataset for saving
        self.svm_model.fit(X, y_encoded)

        # Perform 5-fold cross-validation
        cross_val_scores = cross_val_score(self.svm_model, X, y_encoded, cv=5)
        mean_accuracy = cross_val_scores.mean() * 100  # Convert to percentage

        # Print accuracy results
        # print("Cross-Validation Scores:", cross_val_scores)
        # print("Mean Accuracy:", mean_accuracy, "%")

        return mean_accuracy

    # def save(self, folderPath : str):
    #     # Save the trained model and label encoder
    #     joblib.dump(self.svm_model, f'{folderPath}/svm_model.pkl')
    #     joblib.dump(self.label_encoder, f'{folderPath}/label_encoder_svm.pkl')

        
    #     print("Model saved as 'svm_model.pkl' and label encoder as 'label_encoder_svm.pkl'")