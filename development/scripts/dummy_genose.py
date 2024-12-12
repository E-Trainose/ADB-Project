from serial import Serial
from time import sleep
from random import randint
import numpy as np
import math
from serial import Serial
import struct

command = {
    "init" : 0,
    "ok" : 1,
    "start_sampling" : 100,
    "stop_sampling" : 101
}

def toByte(cmd, val):
    return struct.pack("ii", cmd, val)

def toNumber(msg):
    return struct.unpack("ii", msg)

def sendData():
    ser.write(b'S\n')
     
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

    dts = []

    for d in datas:
        dts.append(str(d))

    ser.write((','.join(dts) + '\n').encode())

    sleep(0.01)

ser = Serial(port="COM2", baudrate=9600, timeout=0.5, write_timeout=0.5)
ser.flush()

isSendData = False

def sendOK():
    sent = 0
    sent += ser.write(toByte(command["ok"], 0))
    sent += ser.write(b"\n")

while True:
    if isSendData == True:
        sendData()
        
    if(ser.readable()):
        recv = ser.read_until(b"\n")

        if(recv == b''):
            continue

        parsed = toNumber(recv[0:8])
        cmd = parsed[0]
        val = parsed[1]

        if(cmd == command["init"]):
            sendOK()
        elif(cmd == command["start_sampling"]):
            isSendData=True
            sendOK()
        elif(cmd == command["stop_sampling"]):
            isSendData=False
            sendOK()


        print(f"command {cmd} value {val}")

