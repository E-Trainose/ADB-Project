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
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
            randint(0, 1000),
        ]

        counter = counter + 1

        dts = []

        for d in datas:
            dts.append(str(d))

        ser.write((','.join(dts) + '\n').encode())

        sleep(0.001)
    except KeyboardInterrupt as e:
        break