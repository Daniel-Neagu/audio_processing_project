import numpy as np
import sounddevice as sd
import serial

#default COM value for my laptop
std_COM = "COM5"

#baudrate of stm32 NUCLEO board
std_baudrate = 38400

#byte size that we'd like to read, keeping it at 1 for now t
bytes_read = 1


serialPort = serial.Serial(
    port=std_COM, baudrate=std_baudrate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE
)
serialString = ""  # Used to hold data coming over UART
while 1:
    # Read data out of the buffer until a carraige return / new line is found
    serialString = serialPort.read(bytes_read)

    # Print the contents of the serial data
    try:
        print(serialString.decode("Ascii"))
    except:
        pass
