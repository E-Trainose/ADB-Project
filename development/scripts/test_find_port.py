import serial.tools.list_ports
from serial import Serial
import struct

command = {
    "init" : 100,
    "ok" : 1
}

def toByte(cmd, val):
    return struct.pack("ii", cmd, val)

def toNumber(msg):
    return struct.unpack("ii", msg)

selectedPort = None
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)
    
    try:
        ser = Serial(port=port.device, baudrate=9600, timeout=0.5, write_timeout=0.5)
        ser.flush()
        
        sent = 0
        sent += ser.write(toByte(command['init'], 120))
        sent += ser.write(b'\n')

        recv = ser.read_until(b'\n')

        print(f"sent : {sent} | recv {recv}")

        parsed = toNumber(recv[0:8])
        cmd = parsed[0]
        val = parsed[1]
        
        if(cmd == command["ok"]):
            selectedPort = port
            break
        
    except Exception as e:
        print(e)

print(selectedPort)