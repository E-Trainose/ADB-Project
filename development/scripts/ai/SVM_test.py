from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import joblib

# Load the saved model and label encoder
model_path = '/home/orin/Documents/svm_model.pkl'
label_encoder_path = '/home/orin/Documents/label_encoder_svm.pkl'

svm_model = joblib.load(model_path)
label_encoder = joblib.load(label_encoder_path)

# Load new unsupervised data
file_path = '/home/orin/Downloads/test_dataset.csv'
data = pd.read_csv(file_path)

# Ensure the feature columns align with the trained model
X_new = data  # Assuming all columns are features in unsupervised test data

# Perform predictions
predicted_classes = svm_model.predict(X_new)

# Decode the predicted class indices to original labels
predicted_labels = label_encoder.inverse_transform(predicted_classes)

# Append predictions to the dataset
data['PREDICTED_LABEL'] = predicted_labels

# Save the predictions to a new file
output_file = '/home/orin/Documents/svm_prediction_result.csv'
data.to_csv(output_file, index=False)

print(f"Predictions saved to '{output_file}'")
