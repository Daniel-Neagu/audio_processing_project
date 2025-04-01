import sys
import PyQt5.QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import *
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtGui import QGuiApplication
import numpy as np
import sounddevice as sd
import serial
import matplotlib.pyplot as plt
import scipy
import sounddevice as sd
from PyQt5.QtCore import QThread, pyqtSignal

windowsize_y= 500
windowsize_x =  500

class SerialReaderThread(QThread):
    sendmsg = pyqtSignal(str)
    def __init__(self):
        super().__init__()

        self.std_COM = "COM5"
        self.std_baudrate = 38400
        self.serialPort = serial.Serial(port=self.std_COM, baudrate=self.std_baudrate, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)

    def run(self):
        #sinewave = np.array([])
        #bellwave = np.array([])
        tracks = np.empty((4, 10), dtype=object)
        for i in range(tracks.shape[0]):
            for j in range(tracks.shape[1]):
                tracks[i,j] = np.zeros(5000)
        
        track_index=0
        index=0
        wave = np.array([])
        readbuffer = False
        uploading=False
        #readbuffer_sine=False
        #readbuffer_bell=False
        #fs = 5000
        while 1: 
            data = self.serialPort.readline().decode().strip()
            #print(data)
            if("signal_sent" in data):
                _,signal_directive = data.split()
                if("go_piano"in signal_directive):
                    self.sendmsg.emit("go_piano")
                elif("go_bells"in signal_directive):
                    self.sendmsg.emit("go_bells")
                elif("go_menu"in signal_directive):
                    self.sendmsg.emit("go_menu")
            elif("play_tracks"in data):
                print("\n".join(f"Element at ({i}, {j}) is None" if tracks[i, j] is None else f"Element at ({i}, {j}) has shape: {tracks[i, j].shape}" for i in range(tracks.shape[0]) for j in range(tracks.shape[1])))
                print(data)
                megatrack = np.sum(np.array([np.concatenate(tracks[i, :]) for i in range(tracks.shape[0]) if all(segment is not None for segment in tracks[i, :])]), axis=0)

                print("playing tracks")
        
                sd.play(megatrack, 5000)
                sd.wait()
                
                    
            elif("record" in data):
                print(data)
            elif("start_uploading_track" in data):
                print(data)
                uploading=True
            elif("done_uploading_track" in data):
                print(data)
                index=0
                self.sendmsg.emit(f"filled {track_index}")
                track_index = (track_index+1)%4
                uploading=False
                
            elif("sending_bell" in data or "sending_sinewave" in data):
                _,freq,duration,fs = data.split()
                freq = int(freq)
                duration = int(duration)
                fs=int(fs)
                readbuffer=True
                if("sending_bell" in data):
                    print("receiving bell information")
                    print(f"bell of type freq: {freq}, duration: {duration}, fs: {fs}")
                elif("sending_sinewave"in data):
                    print("receiving sinewave information")
                    print(f"sinewave of type freq: {freq}, duration: {duration}, fs: {fs}")
            elif(readbuffer):
                if("bell_complete" in data or "sinewave_complete" in data):
                    if("bell_complete" in data):
                        print(f"playing the bell at freq: {freq}, duration: {duration}, fs: {fs}")
                    elif("sinewave_complete" in data):
                        print(f"playing the sinewave at freq: {freq}, duration: {duration}, fs: {fs}")
                    if(freq==0):
                        duration_sound = np.zeros(5000)
                    else:
                        duration_sound = np.tile(wave,int(duration*freq))
                    duration_sound = duration_sound[:5000]
                    if(uploading):
                        tracks[track_index][index] = duration_sound
                        index+=1
                    else:
                        sd.play(duration_sound,fs)
                        sd.wait()
                    if("bell_complete"in data):
                        print(f"bell complete")
                    elif("sinewave_complete"in data):
                        print(f"sinewave complete")
                    readbuffer = False
                    wave = np.array([])
                else:
                    print(f"value is {data}")
                    normdata = (int(data)/2048.0)-2
                    wave = np.append(wave, normdata)

            '''
            elif("sending_bell" in data):
                _,freq,duration,fs = data.split()
                freq = int(freq)
                duration = int(duration)
                fs=int(fs)
                readbuffer_bell=True
                print("receiving bell information")
                print(f"bell of type freq: {freq}, duration: {duration}, fs: {fs}")
                
            elif(readbuffer_bell):
                if("bell_complete"in data):
                    print(f"playing the bell at freq: {freq}, duration: {duration}, fs: {fs}")
                    duration_bellwave = np.tile(bellwave, int(duration*freq))
                    sd.play(duration_bellwave,fs)
                    sd.wait()
                    print(f"bell complete")
                    readbuffer_bell=False
                    bellwave = np.array([])
                else:
                    print(f"value is {data}")
                    normdata = (int(data)/2048.0)-2
                    bellwave = np.append(bellwave, normdata)
            elif("sending_sinewave" in data):
                # data comes in as "sinewave freq duration(s) samplingrate"
                _,freq,duration,fs = data.split()
                freq = int(freq)
                duration = int(duration)
                fs=int(fs)
                readbuffer_sine=True
                print("receiving sinewave information")
                print(f"sinewave of type freq: {freq}, duration: {duration}, fs: {fs}")
            elif(readbuffer_sine):
                if("sinewave_complete" in data):
                    print(f"playing the sinewave at freq: {freq}, duration: {duration}, fs: {fs}")
                    duration_sinewave = np.tile(sinewave, int(duration*freq))
                    sd.play(duration_sinewave, fs)
                    sd.wait()
                    print(f"sinewave complete")
                    readbuffer_sine=False
                    sinewave = np.array([])
                else:
                    print(f"value is {data}")
                    normdata = (int(data)/2048.0)-2
                    sinewave = np.append(sinewave, normdata)'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECE342: Audio Synth Project")
       # self.resize(windowsize_x,windowsize_y)
        #self.setMinimumHeight(windowsize_y)
        #self.setMinimumWidth(windowsize_x)
        self.setFixedSize(QSize(windowsize_x,windowsize_y))
        
        self.setupscreen()

        self.serial_thread = SerialReaderThread()
        self.serial_thread.sendmsg.connect(self.handle_signal)
        self.serial_thread.start()
        
    def handle_signal(self,data):
        if("go_piano" in data):
            self.numpad.setCurrentIndex(1)
        elif("go_menu" in data):
            self.numpad.setCurrentIndex(0)
        elif("go_bells" in data):
            self.numpad.setCurrentIndex(1)
        elif("filled" in data):
            if("0" in data):
                self.trackone.setStyleSheet("background-color: pink")
            elif("1" in data):
                self.tracktwo.setStyleSheet("background-color: pink")
            elif("2" in data):
                self.trackthree.setStyleSheet("background-color: pink")
            elif("3" in data):
                self.trackfour.setStyleSheet("background-color: pink")

        print("signal received")

    def setupscreen(self):
        #create a frame object to encompass the entire screen and allow us to add a layout to it

        self.frame = QFrame()
        self.setCentralWidget(self.frame)

        #vertical layout enconmpasses the tracks area where we can see the audio tracks, and the bottom instruction area where it tells us
        #what the numpad buttons do
        self.layoutV = QVBoxLayout(self.frame)
        self.frame.setStyleSheet("QFrame{background-color: lightblue}")
        self.layoutV.setContentsMargins(0,0,0,0)
        self.layoutV.setSpacing(10)

        #this is the track area and displays FOUR possible tracks, each is horizontal, so this will have to contain
        #4 children widgets which as of now are empty, and therefore this is a horizontal layout
        #if a track is added, the widgets change to a different background indicating there is a track in it
        self.trackslayout_container = QWidget()
        self.trackslayout_container.setFixedHeight(300)
        self.trackslayout = QVBoxLayout(self.trackslayout_container)
        self.layoutV.addWidget(self.trackslayout_container)
        
        #creates the four track widgets and adds them to the trackslayout Vertical Layout
        self.trackone  = track_widget()
        self.tracktwo = track_widget()
        self.trackthree = track_widget()
        self.trackfour = track_widget()
        self.trackslayout.addWidget(self.trackone)
        self.trackslayout.addWidget(self.tracktwo)
        self.trackslayout.addWidget(self.trackthree)
        self.trackslayout.addWidget(self.trackfour)
        #setting padding to the widgets so they don't overlap
        self.trackslayout.setContentsMargins(15,10,15,0)
        self.trackslayout.setSpacing(20)



        #the bottom area includes the instruction area, based on which "menu" you are in it shows you a photo
        #of the numpad and what each button's function is
        #there are two children widgets side by side, one containing the instructions, and one containing the audio info if added
        self.lowerlayout_container = QWidget()
        self.lowerlayout_container.setFixedHeight(200)

        self.lowerlayout = QHBoxLayout(self.lowerlayout_container)
        self.layoutV.addWidget(self.lowerlayout_container)

        self.lowerlayout.setContentsMargins(20,10,20,10)
        self.lowerlayout.setSpacing(50)

        #creates the numpad widget that will show an image of the numpad and cartoon images showing what the buttons' functions are/do
        self.numpad = QStackedWidget()
        self.numpad_main = BackgroundWidget("numpad_main.png")
        self.numpad_piano= BackgroundWidget("pianokeys.png")
        self.numpad.addWidget(self.numpad_main)
        self.numpad.addWidget(self.numpad_piano)

        self.numpad.setFixedSize(150,150)
        self.lowerlayout.addWidget(self.numpad)

        self.fillspace_main = white_widget()
        self.lowerlayout.addWidget(self.fillspace_main)




def track_widget(border_color='white', background_color='lightblue'):
    default = create_style_dict()
    hover = create_style_dict()
    pressed = create_style_dict()
    default["border-color"] = border_color
    default["background-color"] = background_color
    return create_widget(default,hover,pressed)

def white_widget(border_color='', background_color='pink'):
    default = create_style_dict()
    hover = create_style_dict()
    pressed = create_style_dict()
    default["border-color"] = border_color
    default["background-color"] = background_color
    return create_widget(default,hover,pressed)

def numpad_widget(border_color='white', background_color='lightgreen'):
    default = create_style_dict()
    hover = create_style_dict()
    pressed = create_style_dict()
    default["border-color"] = border_color
    default["background-color"] = background_color
    return create_widget(default,hover,pressed)

def create_widget(default,hover,pressed):
    widget = QWidget()
    widget.setStyleSheet(
            "QWidget {"
                f"border-color: {default['border-color']};"
                f"background-color: {default['background-color']};"
                f"border-width: 1px;"
                f"border-style: solid;"
            "}"

    )
    return widget

def create_style_dict():
    return {
        "text": "",
        "color": "",
        "background-color": "",
        "font-size": "",
        "font-family" : "",
        "font-weight" : "",
        "text-align" : "",
        "border-color" : "",
        "border-width" : "",
        "border-style" : "",
        "border-radius" : "",
        "padding" : "",
        "margin" : ""
    }

class BackgroundWidget(QWidget):
    def __init__(self, img_path="numpad_main.png"):
        super().__init__()
        self.pixmap = QPixmap(img_path)  # Replace with your image path
        self.setAutoFillBackground(True)  # Ensure the background is painted
        self.update_background()
    def resizeEvent(self, event):
        # Update the background each time the widget is resized
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        # Get the current size of the widget
        size = self.size()
        # Scale the image to exactly match the widget's size.
        # Qt.IgnoreAspectRatio forces the pixmap to exactly fill the widget (which may distort the image).
        scaled_pixmap = self.pixmap.scaled(size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
        self.setPalette(palette)




if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()  # IMPORTANT!!!!! Windows are hidden by default.

    # Start the event loop.
    app.exec()
