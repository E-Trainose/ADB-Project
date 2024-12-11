import serial.tools.list_ports
from serial import Serial

selectedPort = None
ports = serial.tools.list_ports.comports()
for port in ports:
    print(port.device)
    
    try:
        ser = Serial(port=port.device, baudrate=9600, timeout=0.5, write_timeout=0.5)
        ser.flush()
        
        sent = ser.write(b"init\n")

        recv = ser.read_until(b"\n")

        print(f"sent : {sent} | recv {recv}")
        
        if(recv == b'ok\n'):
            selectedPort = port
            break
        
    except Exception as e:
        print(e)

print(selectedPort)