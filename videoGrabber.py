import getDiceEyes as gde
import time
import cv2


def zoom2ROIRel(zoomVal):
    # 0.5 zoomVal means 50% of the image is shown
    x = 0.5 - zoomVal/2
    y = 0.5 - zoomVal/2
    w = zoomVal
    h = zoomVal

    return (x, y, w, h)


def mainRoutine(camStream, args):

    if args.window:
        print("in window: press      q to quit")
    
    print("in CLI:    press ctrl-c to quit")

    # init Cam interface
    capturing = True
    lastVal = None
    valuePrinted = False
    numFramesSame = 0


    while capturing:

        if camStream.hasNewFrame:
            img = camStream.read()
            img = gde.prepare_image(img, normalise=args.normalise, verbose=args.verbose)
            edges = gde.get_edges(img, dilate_erode_kernel_size=args.kernelSize, dilate_iterations=args.dilateIterations, erode_iterations=args.erodeIterations, verbose=args.verbose)
            contours = gde.get_contours(edges, min_area=args.min_area, max_area=args.max_area, verbose=args.verbose)
            value = gde.get_dice_value(contours, verbose=args.verbose)

            # only print value if value is the same for at least 5 frames
            if value == lastVal:
                numFramesSame += 1
            else:
                numFramesSame = 0
                lastVal = value
                valuePrinted = False

            if numFramesSame >= 5 and not valuePrinted:
                print(value)
                valuePrinted = True


            if args.window:
                img = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
                cv2.putText(img, f"{len(contours)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 2)
                cv2.imshow('img', img)

                keyPressed = cv2.waitKey(1) & 0xFF
                if keyPressed == ord('q'):
                    cv2.destroyAllWindows()
                    camStream.stop()
                    capturing = False
                    quit()



        time.sleep(0.01)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description="get dice value from video", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--window", help="with peeking windows", action="store_true")
    parser.add_argument("--src", type=int, default=0, help="source for webcam")
    parser.add_argument("--width", type=int, default=640, help="width of image")
    parser.add_argument("--height", type=int, default=480, help="height of image")
    parser.add_argument("--min", type=float, default=0.3, help="minimum area of contour in percentage")
    parser.add_argument("--max", type=float, default=0.9, help="maximum area of contour in percentage")
    parser.add_argument("--kernelSize", type=int, default=2, help="kernel size for dilate and erode")
    parser.add_argument("--dilateIterations", type=int, default=3, help="number of dilate iterations")
    parser.add_argument("--erodeIterations", type=int, default=1, help="number of erode iterations")
    # parser.add_argument("--verbose", action="store_true", help="show image with contours")
    parser.add_argument("--normalise", action="store_true", help="normalise image")
    parser.add_argument("--fps", type=int, default=30, help="frames per second")
    parser.add_argument("--zoom", type=float, default=1, help="zoom level")

    args = parser.parse_args()


    args.min_area = args.min/100 * args.width * args.height
    args.max_area = args.max/100 * args.width * args.height
    args.verbose = False

    import os
    unameInfo = os.uname()




    # use webcam on darwin, picam on raspi
    if unameInfo[0].startswith("Darwin"):
        print("on OSX, using webcam")
        WEBCAM = True
    elif unameInfo[4].startswith("armv"):
        print("on raspi, using picam")
        WEBCAM = False
    else:
        print("unknown system, attempting to use webcam.")
        WEBCAM = False
        print("system info:")
        for item in os.uname():
            print(item)

    if WEBCAM:
        PICAM_WIDTH = args.width
        PICAM_HEIGHT = args.height
        import camGrabber.webcamVideoStream as grabber
    else:
        import camGrabber.piVideoStream as grabber


    try:
        while True:
            if WEBCAM:
                print("Initializing USB Camera ....")
                camStream = grabber.VideoStream(
                    resolution=(args.width, args.height), srcID=args.src).start()
                time.sleep(2.0)  # Allow WebCam to initialize
            else:
                print("Initializing Pi Camera ....")
                camStream = grabber.VideoStream(
                    resolution=(globalConf.PICAM_WIDTH,
                                globalConf.PICAM_HEIGHT),
                    hflip=globalConf.PICAM_HFLIP, vflip=globalConf.PICAM_VFLIP,
                    framerate=globalConf.PICAM_FRAMERATE
                ).start()
                time.sleep(1.0)  # Allow PiCamera to inqitialize

            camStream.setFps(args.fps)

            zoom2ROIRelBounds = zoom2ROIRel(args.zoom)
            camStream.setROIRelBounds(*zoom2ROIRelBounds)
            camStream.read()
            mainRoutine(camStream, args)

    except KeyboardInterrupt:
        camStream.stop()

        print("")
        print("+++++++++++++++++++++++++++++++++++")
        print("ctrl-c")
        print(f"{progName} {progVer} - Exiting")
        print("+++++++++++++++++++++++++++++++++++")
        print("")
        quit(0)
