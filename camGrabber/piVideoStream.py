from time import sleep
from threading import Thread
from picamera.array import PiRGBArray
from picamera import PiCamera

class VideoStream:
    def __init__(self, resolution=(320, 240), framerate=10, hflip=False, vflip=False):
        # initialize the camera and stream
        self.camera = PiCamera(
            resolution = resolution, 
            framerate = 10)

        # explanations [here](https://picamera.readthedocs.io/en/release-1.13/api_camera.html)
        # Set ISO to the desired value
        self.camera.iso = 100

        # Wait for automatic gain control to settle
        sleep(2)

        self.camera.framerate = framerate
        # fix gain
        self.camera.shutter_speed = self.camera.exposure_speed
        self.camera.exposure_mode = 'off'

        # set to fixed white balance
        g = self.camera.awb_gains
        print(f"camera awb: {g}")
        self.camera.awb_mode = 'off'
        self.camera.awb_gains = g

        self.camera.hflip = hflip
        self.camera.vflip = vflip
        self.rawFrame = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawFrame,
            format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False
        self.hasNewFrame = False

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def setFps(self, framerate: int):
        self.camera.framerate = framerate
        return self

    def getFps(self):
        return self.camera.framerate

    def getResolution(self):
        # reverse tuple
        return(self.camera.resolution[::-1])

    def setROIRelBounds(self, x=0.0, y=0.0, w=1.0, h=1.0):
        self.camera.zoom = (x, y, w, h)
        return self

    def setROIRelBoundsFromTuple(self, roiRect):
        self.camera.zoom = roiRect

    def getROIBounds(self):
        (x, y, w, h) = self.getROIRelBounds()
        (fW, fH) = self.getResolution()

        upperLeftX = x * fW
        upperLeftY = y * fH
        lowerRightX = upperLeftX + (w * fW)
        lowerRightY = upperLeftY + (h * fH)

        return (int(upperLeftX), int(
            upperLeftY), int(lowerRightX), int(lowerRightY))

    def getROIRelBounds(self):
        return self.camera.zoom

    def update(self):
        # keep looping until thread is stopped
        for currentFrame in self.stream:
            # grab frame from stream
            self.frame = currentFrame.array
            # print("new frame")
            # clear rawFrame to prepare for next capture
            self.rawFrame.truncate(0)

            if self.stopped:
                # stop thread and  release camera resources
                self.stream.close()
                self.rawFrame.close()
                self.camera.close()

            self.hasNewFrame = True

        return self

    def read(self):
        self.hasNewFrame = False
        # return most recent frame
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        return self