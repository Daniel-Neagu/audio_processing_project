import numpy as np
import sounddevice as sd
import serial
import matplotlib.pyplot as plt
import scipy

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
    serialString = ""  # Used to hold data coming over UART
    audio = []
    readbuffer=False
    while 1: 
        #
        data = serialPort.readline().decode().strip()
        print(data)
        if(data == "buffer start"):
            readbuffer=True
            print("reading buffer")
        elif(readbuffer):
            if("buffer complete" in data):
                readbuffer = False
                print("buffer read")
                
                np_audio = np.array(audio)
                #noise_std = np.std(np_audio)
               # print(f"std 0-4095 is {noise_std}")
                np_audio_stdfilt = np_audio.copy()
                noise_std = 80
                np_audio_stdfilt[np.abs(np_audio_stdfilt-2048)<1.5*noise_std] = 2048

                plt.figure()
                plt.plot(np_audio)
                plt.title(f"ADC data over {len(audio)} samples")
                plt.ylabel("ADC Value")
                plt.show()

                plt.figure()
                plt.plot(np_audio_stdfilt)
                plt.title(f"ADC data over {len(audio)} samples")
                plt.ylabel("ADC Value")
                plt.show()

                np_audio_norm = (2048.0-np_audio)/2048.0*5 #change the 5 to 1 
                np_audiofilt_norm = (2048.0-np_audio_stdfilt)/2048.0*5 #change the 5 to 1 
                #noise_std = np.std(np_audio_norm)
                #print(f"std 0-1 is {noise_std}")

                #applying a std filter
                #np_audio[np.abs(np_audio)<1.5*noise_std] = 0

                testing_frequency = 5000
                print("without a filter, and not sampled up")
                sd.play(np_audio_norm, testing_frequency)
                sd.wait()

                print("without a std filter, and not sampled up")
                sd.play(np_audiofilt_norm, testing_frequency)
                sd.wait()

                print(f"playing the upsampled audio at {testing_frequency*2}Hz sample rate")
                np_audio_resample = scipy.signal.resample(np_audiofilt_norm,2*len(np_audiofilt_norm))
                sd.play(np_audio_resample, testing_frequency*2)
                sd.wait()

                print(f"playing the upsampled audio at {testing_frequency*2}Hz sample rate with medfilter")
                np_audio_medfilt = scipy.signal.medfilt(np_audio_resample,kernel_size=3)
                sd.play(np_audio_medfilt, testing_frequency*2)
                sd.wait()

                print("playing the weiner filtered up sampled audio")
                np_audio_weiner = scipy.signal.wiener(np_audio_resample)
                sd.play(np_audio_weiner, testing_frequency*2)
                sd.wait()

                print(f"playing the poly upsampled audio at {testing_frequency*2}Hz sample rate")
                np_audio_resample_poly = scipy.signal.resample_poly(np_audiofilt_norm,up=2,down=1)
                sd.play(np_audio_resample_poly, testing_frequency*2)
                sd.wait()

                print("playing the weiner filtered poly up sampled audio")
                np_audio_weiner = scipy.signal.wiener(np_audio_resample_poly)
                sd.play(np_audio_weiner, testing_frequency*2)
                sd.wait()

                print("playing the moving avg audio with 3 neighbours no upsample")
                np_audio_movingavg_noup3 = np.convolve(np_audiofilt_norm, np.ones(3)/3, mode='same')
                sd.play(np_audio_movingavg_noup3, testing_frequency)
                sd.wait()
                print("playing the moving avg audio with 5 neighbours no upsample")
                np_audio_movingavg_noup5 = np.convolve(np_audiofilt_norm, np.ones(5)/5, mode='same')
                sd.play(np_audio_movingavg_noup5, testing_frequency)
                sd.wait()

                print("playing the moving avg audio with 3 neighbours, poly upsample first")
                np_audio_movingavg_polyup3 = np.convolve(np_audio_resample_poly, np.ones(3)/3, mode='same')
                sd.play(np_audio_movingavg_polyup3, testing_frequency*2)
                sd.wait()

                print("playing the moving avg audio with 5 neighbours, poly upsample first")
                np_audio_movingavg_polyup5 = np.convolve(np_audio_resample_poly, np.ones(5)/5, mode='same')
                sd.play(np_audio_movingavg_polyup5, testing_frequency*2)
                sd.wait()

                print("playing the moving avg audio with 3 neighbours, poly upsample after ")
                np_audio_movingavg_polyup3after = scipy.signal.resample_poly(np_audio_movingavg_noup3,up=2,down=1)
                sd.play(np_audio_movingavg_polyup3after, testing_frequency*2)
                sd.wait()

                print("playing the moving avg audio with 5 neighbours, poly upsample after")
                np_audio_movingavg_polyup5after = scipy.signal.resample_poly(np_audio_movingavg_noup5,up=2,down=1)
                sd.play(np_audio_movingavg_polyup5after, testing_frequency*2)
                sd.wait()
            
                np_audio=[]
                np_audio_norm=[]
                np_audio_stdfilt=[]
                audio=[]
                noise_std = 0
            else:
                audio.append(int(data))
            
            
readbytes()
        
        

samplerate = 1920#44100   # Sample rate in Hz
channels = 1         # Mono audio
sample_format = 'float32'  # sounddevice-compatible format

def callback(outdata, frames, time, status):
    if status:
        print("Stream status:", status)

    # Calculate the number of bytes needed (2 bytes per uint16 sample)
    bytes_needed = frames * channels * 2
    data = serialPort.read(bytes_needed)

    # If less data is received, pad with zeros
    if len(data) < bytes_needed:
        data += b'\x00' * (bytes_needed - len(data))

    # Convert bytes to uint16 array
    audio_uint16 = np.frombuffer(data, dtype=np.uint16)

    # Convert to float32 in the range [-1.0, 1.0]
    audio_float32 = (audio_uint16.astype(np.float32) - 2048.0) / 2048.0

    # Reshape for output
    try:
        outdata[:] = audio_float32.reshape(-1, channels)
    except ValueError:
        outdata.fill(0)



'''# Create and start the audio stream
stream = sd.OutputStream(
    channels=channels,
    samplerate=samplerate,
    dtype=sample_format,
    callback=callback
)
stream.start()

try:
    while True:
        sd.sleep(1000)  # Keeps the main thread alive
except KeyboardInterrupt:
    print("Stopping stream...")
finally:
    stream.stop()
    stream.close()
    serialPort.close()'''

readbytes()
