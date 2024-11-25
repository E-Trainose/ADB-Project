import serial
import csv
import time
import os
import sys



# Configure serial connection
ser = serial.Serial('COM6', 9600, timeout=1)  # Change 'COM18' to your actual COM port
time.sleep(2)  # Allow time for the serial connection to stabilize
#sudo chmod a+wr /dev/ttyUSB0
# Specify the CSV file path
filename = os.path.join('C:/Users/ILYAZRA/Documents/tugas/ADB/GUI/ADB-Project/development/devGUI/data/dataset_valve_alkohol10.csv')
# Define the aroma name to be added to each data entry
aroma_name = "takecoba"

# Open the CSV file for writing
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header with an additional column for "Aroma"
    writer.writerow(['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8', 'TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3', 'AROMA'])

    print("Waiting for 'S' command from Arduino to start collecting data...")

    # Wait for 'S' command from Arduino to start collecting data
    while True:
        try:
            # Read a line from the serial
            command = ser.readline().decode('ISO-8859-1').strip()
            if command == 'S':
                print("Received 'S' command. Starting data collection...")
                break  # Exit the loop to start collecting data
        except Exception as e:
            print(f"Error reading from serial: {e}")

    # Counter to track the number of data points saved
    data_count = 0
    max_data_count = 2355  # Maximum number of data entries to collect 2355

    while data_count < max_data_count:
        try:
            # Read data from the serial port
            data = ser.readline().decode('ISO-8859-1').strip()  # Use 'ISO-8859-1' to avoid decoding errors
            if data:
                # Split the data into a list of strings
                sensor_values = data.split(',')

                # Convert the sensor values to float or int (use float here)
                sensor_values = [float(value) for value in sensor_values]

                print(sensor_values)  # Optional: Print the data to the console

                # Append the aroma name to the data (this stays a string)
                sensor_values.append(aroma_name)

                # Write the data to the CSV
                writer.writerow(sensor_values)

                # Increment the counter
                data_count += 1

        except KeyboardInterrupt:
            print("Program interrupted.")
            break
        except ValueError:
            print(f"Error converting data to float: {data}")


print(f"Program finished. Data saved: {data_count} rows.")
# Close the serial connection
ser.close()
