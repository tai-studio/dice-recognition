import cv2
from threading import Thread

class VideoStream:
    def __init__( self, resolution = (320, 240), srcID=0 ):
        # initialize camera stream and read first frame
        # self.stream = CAM_SRC
        self.stream = cv2.VideoCapture(srcID)

        # config
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        # self.stream.set(cv2.CAP_PROP_FPS, <Frame rate.>)

        self.stream.set(cv2.CAP_PROP_BRIGHTNESS, 100)
        self.stream.set(cv2.CAP_PROP_CONTRAST, 100)
        self.stream.set(cv2.CAP_PROP_EXPOSURE, 100)
        # self.stream.set(cv2.CAP_PROP_SATURATION, <Saturation of the image (only for cameras).>)
        # self.stream.set(cv2.CAP_PROP_HUE, <Hue of the image (only for cameras).>)
        # self.stream.set(cv2.CAP_PROP_GAIN, <Gain of the image (only for cameras).>)
        # self.stream.set(cv2.CAP_PROP_CONVERT_RGB, <Boolean flags indicating whether images should be converted to RGB.>)

        # initialise ROI values
        self.setROIRelBounds()

        self.__grabFrame()

        self.hasNewFrame = False
        self.stopped = False

    def start(self):
        # start thread to read frames from video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def setFps(self, framerate: int):
        self.stream.set(cv2.CAP_PROP_FPS, framerate )
        return self

    def getFps(self):
        return self.stream.get(cv2.CAP_PROP_FPS)


    def getResolution(self):
        width = self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return (height, width)

    def setROIRelBounds(self, x=0.0, y=0.0, w=1.0, h=1.0):
        if( (x != 0.0) or (y != 0.0) or (w != 1.0) or (h != 1.0)):
            self.usesROI = True
        else:
            self.usesROI = False


        self.__roiRelBounds = (x, y, w, h)
        print(f"setROIRelBounds({self.__roiRelBounds})")
        (fW, fH) = self.getResolution()
        upperLeftX = x * fW
        upperLeftY = y * fH
        lowerRightX = upperLeftX + (w * fW)
        lowerRightY = upperLeftY + (h * fH)
        self.__roiBounds = (int(upperLeftX), int(
            upperLeftY), int(lowerRightX), int(lowerRightY))

        return self

    def setROIRelBoundsFromTuple(self, roiRect):
        self.setROIRelBounds(roiRect[0], roiRect[1], roiRect[2], roiRect[3])

    def getROIBounds(self):
        return self.__roiBounds

    def getROIRelBounds(self):
        return self.__roiRelBounds

    def update(self):
        # looping until thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                    return

            # otherwise, read the next frame from the stream
            self.__grabFrame()

            self.hasNewFrame = True

    def read(self):
        # return most recent frame
        self.hasNewFrame = False
        return self.frame

    def stop(self):
        # stop thread ASAP
        self.stopped = True
        self.stream.release()

    def __grabFrame(self):
        (self.grabbed, self.rawFrame) = self.stream.read()

        if self.usesROI:
            # print("uses roi")
            (x0, y0, x1, y1) = self.getROIBounds()
            self.frame = self.rawFrame[x0:x1, y0:y1]
        else:
            self.frame = self.rawFrame
        return self
