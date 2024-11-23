import serial
import csv
import pandas as pd
import numpy as np

"""
dashboard
select default
take data sample:
    select port (COM?)
    create DataCollector(port COM?) as dCol
    dCol.collect(amount=int?) as collected
    dCol.save(filename=?)
    
    done
"""

class DataCollector:
    def __init__(self, port : str = "", amount : int = 0):
        self.port = port
        self.baudrate = 9600
        self.timeout = 1
        self.amount = amount

        self.sensor_values = []

        self.sensor_headers = ['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8', 'TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3']

    def initialize(self):
        self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout)

    def reset(self):
        self.sensor_values = []

    def collect(self):
        print("Waiting for 'S' command from Arduino to start collecting data...")

        # Wait for 'S' command from Arduino to start collecting data
        start_collecting = False
        while not start_collecting:
            try:
                # Read a line from the serial
                command = self.serial.readline().decode('ISO-8859-1').strip()
                if command == 'S':
                    print("Received 'S' command. Starting data collection...")
                    start_collecting = True  # Exit the loop to start collecting data
            except Exception as e:
                print(f"Error reading from serial: {e}")

        # Counter to track the number of data points saved
        data_count = 0
        num_of_wave_cycle = self.amount
        wave_cycle_count = 156
        max_data_count = num_of_wave_cycle * wave_cycle_count  # Maximum number of data entries to collect 2355

        while data_count < max_data_count:
            try:
                # Read data from the serial port
                data = self.serial.readline().decode('ISO-8859-1').strip()  # Use 'ISO-8859-1' to avoid decoding errors
                if data and data != 'S':
                    # Split the data into a list of strings
                    sensor_values = data.split(',')

                    sensor_values = [int(i) for i in sensor_values]

                    self.sensor_values.append(sensor_values)

                    # Increment the counter
                    data_count += 1

            except KeyboardInterrupt:
                print("Program interrupted.")
                break
            except ValueError:
                print(f"Error converting data to float: {data}")

    def getDataFrame(self):
        data = pd.DataFrame()
        sensor_values_np = np.array(self.sensor_values).transpose()
        print(f"shape {sensor_values_np.shape}")

        for i in range(0, len(self.sensor_headers)):
            header = self.sensor_headers[i]
            value = sensor_values_np[i]
            data[header] = value

        return data

    def save(self, filename : str):
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header with an additional column for "Aroma"
            writer.writerow(self.sensor_headers)

            writer.writerows(self.sensor_values)
