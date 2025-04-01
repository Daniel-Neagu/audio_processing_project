import numpy as np
import sounddevice as sd


std_fs = 44100

notes_freq = {
    "C": [16.35, 32.70, 65.41, 130.81, 261.63, 523.25, 1046.50, 2093.00, 4186.01],
    "C#": [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
    "Db": [17.32, 34.65, 69.30, 138.59, 277.18, 554.37, 1108.73, 2217.46, 4434.92],
    "D":  [18.35, 36.71, 73.42, 146.83, 293.66, 587.33, 1174.66, 2349.32, 4698.63],
    "D#": [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
    "Eb": [19.45, 38.89, 77.78, 155.56, 311.13, 622.25, 1244.51, 2489.02, 4978.03],
    "E":  [20.60, 41.20, 82.41, 164.81, 329.63, 659.25, 1318.51, 2637.02, 5274.04],
    "F":  [21.83, 43.65, 87.31, 174.61, 349.23, 698.46, 1396.91, 2793.83, 5587.65],
    "F#": [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
    "Gb": [23.12, 46.25, 92.50, 185.00, 369.99, 739.99, 1479.98, 2959.96, 5919.91],
    "G":  [24.50, 49.00, 98.00, 196.00, 392.00, 783.99, 1567.98, 3135.96, 6271.93],
    "G#": [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
    "Ab": [25.96, 51.91, 103.83, 207.65, 415.30, 830.61, 1661.22, 3322.44, 6644.88],
    "A":  [27.50, 55.00, 110.00, 220.00, 440.00, 880.00, 1760.00, 3520.00, 7040.00],
    "A#": [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
    "Bb": [29.14, 58.27, 116.54, 233.08, 466.16, 932.33, 1864.66, 3729.31, 7458.62],
    "B":  [30.87, 61.74, 123.47, 246.94, 493.88, 987.77, 1975.53, 3951.07, 7902.13],
    "rest" : [0]
}


def playsine(duration=5.0, frequency=440.0, amplitude=0.5, fs=44100):
    # Parameters for the sine wave
    #duration (seconds)
    #fs (sampling rate in Hz)
    #frequency (frequency of the sine wave in Hz (A4 note))
    #amplitude (amplitude of the sine wave)

    # Generate time values and the sine wave signal
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

    # Play the sine wave
    sd.play(sine_wave, fs)
    sd.wait()  # Wait until playback is finished


def playsong(sounds):
    #notes must be provided in the following format "[[note, duration, amplitude],[note, duration, amplitude]...]"
    #note must be of the form (note, octave)
    #if incorrectly added, we will play nothing for 2 seconds
    for sound in sounds:
        try:
            note,octave = sound[0]
            duration = sound[1]
            amplitude = sound[2]
            playsine(duration=duration,amplitude=amplitude, frequency = notes_freq[note][octave])
        except:
            playsine(amplitude=0, duration=2, frequency=0)




playsine(duration=1,amplitude=1, frequency=440,fs=5000)