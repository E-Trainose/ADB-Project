import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Load your CSV file
data = pd.read_csv('C:/Users/ILYAZRA/Documents/tugas/ADB/new/dataset_valve_teh1.csv')

# Function to plot one wave cycle from peak to peak for a given sensor
def plot_wave_cycle(sensor_name):
    if sensor_name in data.columns:
        # Get the sensor data
        sensor_data = data[sensor_name]
        
        # Identify peaks
        peaks, _ = find_peaks(sensor_data)
        
        # Ensure there are at least two peaks to plot a wave cycle
        if len(peaks) > 1:
            # Find the first and second peaks
            first_peak = peaks[0]
            second_peak = peaks[1]
            
            # Extract the data for one wave cycle (between the two peaks)
            one_wave_cycle = sensor_data[first_peak:second_peak + 1]
            
            # Plot the wave cycle
            plt.figure(figsize=(10, 6))
            plt.plot(one_wave_cycle, label=f'One Wave Cycle ({sensor_name})', color='blue')
            plt.title(f'One Full Wave Cycle from Peak to Peak ({sensor_name})')
            plt.xlabel('Time (relative index)')
            plt.ylabel(f'Sensor Reading ({sensor_name})')
            plt.legend()
            plt.grid(True)
            plt.show()
            
            # Display the extracted data points for one wave cycle
            print(one_wave_cycle)
        else:
            print(f"Not enough peaks found in {sensor_name} data to plot a wave cycle.")
    else:
        print(f"Sensor '{sensor_name}' not found in the dataset.")

# Input sensor name from user
sensor_name = input("Enter the sensor name (e.g., MQ8, TGS2600): ")
plot_wave_cycle(sensor_name)
