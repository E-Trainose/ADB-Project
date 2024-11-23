from serial import Serial
from time import sleep
from random import randint


ser = Serial(port='COM1', baudrate=9600)

ser.write(b'S\n')

while True:
    try:
        datas = [
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100),
            randint(0, 100)
        ]
        dts = []

        for d in datas:
            dts.append(str(d))

        ser.write((','.join(dts) + '\n').encode())

        sleep(0.001)
    except KeyboardInterrupt as e:
        break