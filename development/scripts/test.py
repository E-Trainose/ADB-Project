import struct
import time
from serial import Serial

ser = Serial(port="COM15", baudrate=9600)
ser.flush()

time.sleep(2)

print("send")
packet = bytearray()
packet.append(0x64)
packet.append(0x00)
packet.append(0x00)
packet.append(0x00)

packet.append(0x00)
packet.append(0x00)
packet.append(0x00)
packet.append(0x00)

packet.append(0x0a)

sent = 0
sent += ser.write(packet)

while(1):
    try:
        recv = ser.readline()
        print(f"sent : {sent} received : {recv}")
    except KeyboardInterrupt as e:
        break