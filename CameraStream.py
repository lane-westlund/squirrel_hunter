import os
from threading import Thread
import cv2

class CameraStream:
    def __init__(self, resolution=(1024, 768), framerate=32):

        #init code
        self.pi = False
        if os.uname()[1] == "raspberrypi":
            from picamera.array import PiRGBArray
            from picamera import PiCamera
            self.pi = True
            self.camera = PiCamera()
            self.camera.resolution = resolution
            self.camera.framerate = framerate
            self.rawCapture = PiRGBArray(self.camera, size=resolution)
            self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)

        else:
            self.camera = cv2.VideoCapture(0)

        self.frame = None
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        if self.pi == True:
            for f in self.stream:
                self.frame = frame.array
                self.rawCapture.truncate(0)

                if self.stopped:
                        self.stream.close()
                        self.rawCapture.close()
                        self.camera.close()
                        return
        else:
            while self.stopped == False:
                (grabbed, self.frame) = self.camera.read()
            self.camera.release()
            return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True