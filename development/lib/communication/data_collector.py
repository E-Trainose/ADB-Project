import serial
from lib.communication.communication import Communication
import csv
import pandas as pd
import numpy as np
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

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

class DataCollector(QObject):
    progress = pyqtSignal(int)

    def __init__(self, port : str = "", amount : int = 0):
        super().__init__()
        self.port = port
        self.baudrate = 9600
        self.timeout = 1
        self.amount = amount

        self.sensor_values = []

        self.sensor_headers = ['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8', 'TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3']

    def initialize(self):
        self.serial = serial.Serial(port=self.port, baudrate=self.baudrate, timeout=self.timeout, write_timeout=self.timeout)
        self.serial.write(Communication.toByte(Communication.Command.INIT, 0))

        if(self.isOK()):
            return
        else:
            raise Exception("Genose not responding")
        
        
    def isOK(self):
        recv = self.serial.read_until(b"\n")
        recv = Communication.toNumber(recv[0:8])
        
        if(recv[0] == Communication.Command.OK):
            return True
        else:
            return False
        
    def reset(self):
        self.sensor_values = []

    def collect(self):
        self.serial.write(Communication.toByte(Communication.Command.START_SAMPLING, 0))

        if(self.isOK() == False):
            raise Exception("Genose not responding")
        
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

                    progress = int((data_count / max_data_count) * 100)
                    self.progress.emit(progress)
                    # Increment the counter
                    data_count += 1

            except KeyboardInterrupt:
                print("Program interrupted.")
                break
            except ValueError:
                print(f"Error converting data to float: {data}")

        self.serial.write(Communication.toByte(Communication.Command.STOP_SAMPLING, 0))

        if(self.isOK() == False):
            raise Exception("Genose not responding")

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



class DataCollectionThread(QThread):
    finished = pyqtSignal(pd.DataFrame)
    progress = pyqtSignal(int)

    def on_progress(self, progress):
        self.progress.emit(progress)

    def setPort(self, port: str):
        self.port = port

    def setAmount(self, amount: int):
        self.amount = amount

    def run(self):
        try:
            print(f"Collecting from port {self.port} with amount {self.amount}")
            # Pass the amount parameter when initializing DataCollector
            self.data_collector = DataCollector(port=self.port, amount=self.amount)
            self.data_collector.progress.connect(self.on_progress)
            self.data_collector.initialize()
            self.data_collector.collect()
            
            # self.data_collector.save(filename='file.csv')
            datas = self.data_collector.getDataFrame()

        except FileNotFoundError as e:
            print(f"cant access port {self.port}")

        except Exception as e:
            print(f"Error during data collection: {e}")

        finally:
            self.finished.emit(datas)