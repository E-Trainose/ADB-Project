from serial import Serial
from time import sleep
from random import randint
import numpy as np
import math

ser = Serial(port='COM1', baudrate=9600)

ser.write(b'S\n')

counter = 0
MAX_COUNTER = 1000
sin_inputs = np.linspace(0, 3.14, MAX_COUNTER)

while True:
    try:
        if(counter >= MAX_COUNTER):
            counter = 0
        
        siny = math.sin(sin_inputs[counter])
                         
        datas = [
            int(siny * 10),
            int(siny * 100),
            int(siny * 150),
            int(siny * 200),
            int(siny * 250),
            int(siny * 300),
            int(siny * 350),
            int(siny * 400),
            int(siny * 500),
            int(siny * 600),
        ]

        counter = counter + 1

        dts = []

        for d in datas:
            dts.append(str(d))

        ser.write((','.join(dts) + '\n').encode())

        sleep(0.001)
    except KeyboardInterrupt as e:
        break