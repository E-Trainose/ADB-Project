from serial import Serial

ser = Serial(port="COM2", baudrate=9600, timeout=0.5, write_timeout=0.5)
ser.flush()

while True:
    if(ser.readable()):
        recv = ser.read_until(b"\n")

        if(recv == b''):
            continue

        if(recv == b'init\n'):
            sent = ser.write(b"ok\n")
            print("sent")

        print(f"recv {recv}")