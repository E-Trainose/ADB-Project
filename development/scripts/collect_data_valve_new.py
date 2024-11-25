import serial
import csv
import time
import os

# Configure serial connection
# sudo chmod a+wr /dev/ttyUSB0
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Change '/dev/ttyUSB0' to your actual COM port
time.sleep(2)  # Allow time for the serial connection to stabilize

# Specify the CSV file path
filename = os.path.join('/home/orin/Documents/Dataset/data_valve_test.csv')

# Define the aroma name to be added to each data entry
aroma_name = "010"

# Open the CSV file for writing
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header with an additional column for "Aroma"
    writer.writerow(['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8', 'TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3', 'AROMA'])

    print("Waiting for 'S' command from Arduino to start collecting data...")

    # Wait for the first 'S' command from Arduino to start collecting data
    start_collecting = False
    while not start_collecting:
        try:
            # Read a line from the serial
            command = ser.readline().decode('ISO-8859-1').strip()
            if command == 'S':
                print("Received 'S' command. Starting data collection...")
                start_collecting = True  # Set the flag to True to start collecting data
        except Exception as e:
            print(f"Error reading from serial: {e}")

    # Counter to track the number of data points saved
    data_count = 0
    num_of_wave_cycle = 3             
    wave_cycle_count = 156
    max_data_count = num_of_wave_cycle * wave_cycle_count  # Maximum number of data entries to collect

    while data_count < max_data_count:
        try:
            # Read data from the serial port
            data = ser.readline().decode('ISO-8859-1').strip()  # Use 'ISO-8859-1' to avoid decoding errors
            if data and data != 'S':  # Ignore 'S' commands after the first one
                # Split the data into a list
                sensor_values = data.split(',')
                print(sensor_values)  # Optional: Print the data to the console

                # Append the aroma name to the data
                sensor_values.append(aroma_name)

                # Write the data to the CSV
                writer.writerow(sensor_values)

                # Increment the counter
                data_count += 1

        except KeyboardInterrupt:
            print("Program interrupted.")
            break

print(f"Program finished. Data saved: {data_count} rows.")
# Close the serial connection
ser.close()
