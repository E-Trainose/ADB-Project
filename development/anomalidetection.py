import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import zscore
from scipy.ndimage import gaussian_filter1d
import seaborn as sns

# Load the dataset
file_path = "C:/Users/ILYAZRA/Documents/tugas/ADB/new/dataset_valve_1.csv"
df = pd.read_csv(file_path)

# Select sensor columns (excluding the 'AROMA' column)
sensor_columns = df.columns[:-1]

# Apply Gaussian smoothing to the sensor data
smoothed_df = df[sensor_columns].apply(lambda x: gaussian_filter1d(x, sigma=2))

# Calculate Z-scores for each sensor to detect anomalies
z_scores = smoothed_df.apply(zscore)

# Define a threshold for anomaly detection
anomaly_threshold = 3

# Identify anomalies where the Z-score is greater than the threshold
anomalies = (z_scores.abs() > anomaly_threshold)

# Plotting all sensor readings with anomalies highlighted
plt.figure(figsize=(14, 8))

# Plot all smoothed sensor readings
for sensor in sensor_columns:
    plt.plot(smoothed_df.index, smoothed_df[sensor], label=sensor)

# Highlight anomalies in red
for sensor in sensor_columns:
    anomaly_indices = smoothed_df.index[anomalies[sensor]]
    plt.scatter(anomaly_indices, smoothed_df.loc[anomaly_indices, sensor], color='red', s=10, label=f'Anomaly ({sensor})' if len(anomaly_indices) > 0 else "")

# Adding labels and title
plt.xlabel('Index')
plt.ylabel('Sensor Readings')
plt.title('Gaussian Smoothed Sensor Data with Anomalies Highlighted')
plt.legend()

# Display the plot
plt.show()

# Correlation analysis on smoothed data
correlation_matrix = smoothed_df.corr()
plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5, vmin=-1, vmax=1)
plt.title('Correlation Matrix of Gaussian Smoothed Sensor Data')
plt.show()

# Find the strongest correlations
correlation_matrix_no_diag = correlation_matrix.copy()
np.fill_diagonal(correlation_matrix_no_diag.values, 0)
strongest_positive_correlation = correlation_matrix_no_diag.max().max()
strongest_negative_correlation = correlation_matrix_no_diag.min().min()
positive_pair = correlation_matrix_no_diag.stack().idxmax()
negative_pair = correlation_matrix_no_diag.stack().idxmin()

print("Strongest Positive Correlation:", positive_pair, "with correlation of", strongest_positive_correlation)
print("Strongest Negative Correlation:", negative_pair, "with correlation of", strongest_negative_correlation)