from serial import Serial
import struct

command = {
    "init" : 0,
    "ok" : 1
}

def toByte(cmd, val):
    return struct.pack("ii", cmd, val)

def toNumber(msg):
    return struct.unpack("ii", msg)

ser = Serial(port="COM2", baudrate=9600, timeout=0.5, write_timeout=0.5)
ser.flush()

while True:
    if(ser.readable()):
        recv = ser.read_until(b"\n")

        if(recv == b''):
            continue

        parsed = toNumber(recv[0:8])
        cmd = parsed[0]
        val = parsed[1]

        if(cmd == command["init"]):
            sent = 0
            sent += ser.write(toByte(command["ok"], 0))
            sent += ser.write(b"\n")
            print("sent {sent}")

        print(f"command {cmd} value {val}")