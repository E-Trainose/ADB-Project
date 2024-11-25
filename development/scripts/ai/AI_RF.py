from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
import pandas as pd
import joblib

# Load the dataset
file_path = '/home/orin/Downloads/Processed_Sensor_Data.csv'
data = pd.read_csv(file_path)

# Split features and label
X = data.drop(columns=['LABEL'])
y = data['LABEL']

# Encode the labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Define the Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_model.fit(X, y_encoded)

# Perform 5-fold cross-validation
cross_val_scores = cross_val_score(rf_model, X, y_encoded, cv=5)
mean_accuracy = cross_val_scores.mean() * 100  # Convert to percentage

# Save the trained model and label encoder
joblib.dump(rf_model, '/home/orin/Documents/random_forest_model.pkl')
joblib.dump(label_encoder, '/home/orin/Documents/label_encoder_rf.pkl')

# Print accuracy results
print("Cross-Validation Scores:", cross_val_scores)
print("Mean Accuracy:", mean_accuracy, "%")
print("Model saved as 'random_forest_model.pkl' and label encoder as 'label_encoder_rf.pkl'")
