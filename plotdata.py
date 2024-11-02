import pandas as pd
import matplotlib.pyplot as plt

# Load your CSV file
data = pd.read_csv('C:/Users/ILYAZRA/Documents/tugas/ADB/new/new_teh.csv')

# Function to plot the selected sensor data
def plot_sensor(sensor_name):
    if sensor_name in data.columns:
        # Get the sensor data
        sensor_data = data[sensor_name]

        # Plot the entire sensor data from start to end
        plt.figure(figsize=(10, 6))
        plt.plot(sensor_data, label=f'{sensor_name} Sensor Data', color='blue')
        plt.title(f'{sensor_name} Sensor Data (Start to End)')
        plt.xlabel('Time (relative index)')
        plt.ylabel(f'Sensor Reading ({sensor_name})')
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        print(f"Sensor '{sensor_name}' not found in the dataset.")

# Input sensor name from user
sensor_name = input("Enter the sensor name (e.g., MQ8, TGS2600): ")
plot_sensor(sensor_name)
