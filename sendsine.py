import numpy as np
import sounddevice as sd
import serial
import matplotlib.pyplot as plt
import scipy
import sounddevice as sd


# Default COM value for my laptop
std_COM = "COM5"

# Baudrate of STM32 NUCLEO board
std_baudrate = 38400

# Number of bytes to read at a time
bytes_read = 1

# Open serial port
serialPort = serial.Serial(
    port=std_COM, baudrate=std_baudrate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)

def readbytes():
    sinewave = np.array([])
    readbuffer=False
    #fs = 5000
    while 1: 
        data = serialPort.readline().decode().strip()
        #print(data)
        if("sending_sinewave" in data):
            # data comes in as "sinewave freq duration(s) samplingrate"
            _,freq,duration,fs = data.split()
            freq = int(freq)
            duration = int(duration)
            fs=int(fs)
            readbuffer=True
            print("receiving sinewave information")
            print(f"sinewave of type freq: {freq}, duration: {duration}, fs: {fs}")
        elif(readbuffer):
            if("sinewave complete" in data):
                print(f"playing the sinewave at freq: {freq}, duration: {duration}, fs: {fs}")
                duration_sinewave = np.tile(sinewave, int(duration*freq))
                sd.play(duration_sinewave, fs)
                sd.wait()
                print(f"sinewave_complete")
                readbuffer=False
                sinewave = np.array([])
            else:
                print(f"value is {data}")
                normdata = (int(data)/2048.0)-2
                sinewave = np.append(sinewave, normdata)

readbytes()