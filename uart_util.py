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

def readbytes():

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

 
samplerate = 44100   # Sample rate in Hz
channels = 1         # Number of channels
sample_format = np.uint16  # Matches the uint16_t data sent via UART

def callback(outdata, frames, time, status):
    if status:
        print("Stream status:", status)
    # Calculate number of bytes needed (2 bytes per sample)
    bytes_needed = frames * channels * 2  
    data = serialPort.read(bytes_needed)
    
    # If less data is received, pad with zeros
    if len(data) < bytes_needed:
        data += b'\x00' * (bytes_needed - len(data))
    
    # Convert the raw bytes into a NumPy array of uint16
    audio_data = np.frombuffer(data, dtype=sample_format)
    
    # Optionally, if your meaningful range is only 12 bits (0-4095), mask the data:
    # audio_data = audio_data & 0x0FFF

    # Reshape the array to match the output shape: (frames, channels)
    try:
        outdata[:] = audio_data.reshape(-1, channels)
    except ValueError:
        outdata.fill(0)

# Create and start the audio stream with the specified data type
stream = sd.OutputStream(channels=channels, samplerate=samplerate, dtype=sample_format, callback=callback)
stream.start()

try:
    while True:
        sd.sleep(1000)  # Keeps the main thread alive
except KeyboardInterrupt:
    print("Stopping stream...")
finally:
    stream.stop()
    stream.close()
    serialPort.close()