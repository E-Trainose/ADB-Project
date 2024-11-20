from serial import Serial
from time import sleep


ser = Serial(port='COM1', baudrate=9600)

datas = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
dts = []

for d in datas:
    dts.append(str(d))

ser.write(b'S\n')

while True:
    try:
        ser.write((','.join(dts) + '\n').encode())

        sleep(1)
    except KeyboardInterrupt as e:
        break