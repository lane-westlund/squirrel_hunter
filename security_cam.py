# This file has two main purposes
# 1) To be run on a raspberry pi long term to gather
#    test images to the output_dir.  The goal is simply
#    to look for motion, save the image, and sort them
#    later for feeding into a machine learning system
#
# 2) To serve as a debug platform to evaluate various
#    motion capture and/or machine learning algorithms
#
# It is still somewhat crude...

import numpy as np
import cv2
import time
import imutils
import datetime
import os
import argparse


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
args = vars(ap.parse_args())

pi = False
if os.uname()[1] == "raspberrypi":
    from picamera.array import PiRGBArray
    from picamera import PiCamera
    pi = True

if pi == True:
    camera = PiCamera()
    camera.resolution = (1024, 768)
    camera.start_preview()
    time.sleep(2)
    stream = PiRGBArray(camera)
    #rawCapture = PiRGBArray(camera, size=(640, 480))
else:
    if args.get("video", None) is None:
        camera = cv2.VideoCapture(0)
        # let the camera warm up
        time.sleep(2)
    else:
        camera = cv2.VideoCapture(args["video"])




#fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
#fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

movement_detected = False

try:
    os.makedirs('output_dir')
except OSError:
    pass

mark_time = datetime.datetime.now()
frame_number = 0
frame_writes = 0

while True:

    if (datetime.datetime.now() - mark_time).seconds >= 10:
        fps = frame_number / float(((datetime.datetime.now() - mark_time).seconds))
        print("frames per second: " + str(fps) + " writes: " + str(frame_writes))
        mark_time = datetime.datetime.now()
        frame_number = 0
        frame_writes = 0

    frame_number = frame_number + 1

    if pi == True:
        camera.capture(stream, format='bgr')
        frame_orrig = stream.array
        grabbed = True
    else:
        (grabbed, frame_orrig) = camera.read()

    # if we didn't read
    if not grabbed:
        break;

    #sizing stuff
    frame = imutils.resize(frame_orrig, width=(500))
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #gray = cv2.GaussianBlur(gray, (21,21), 0)

    fgmask = fgbg.apply(frame)

    thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
    #dilate the threshold image to fill in holes, then find contours
    #on the threshold image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #loop over the contours
    movement_detected = False

    for c in cnts:
        if cv2.contourArea(c) < 500:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        movement_detected = True
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2 )

   # cv2.imshow('mask', fgmask)
   # cv2.imshow('frame', frame)
    if(movement_detected == True):
        dt = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        cv2.imwrite('output_dir/'+dt+'_hint.png', frame)
        cv2.imwrite('output_dir/'+dt+'_full.png', frame_orrig)
        frame_writes = frame_writes + 1
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    if pi == True:
        stream.truncate(0)

camera.release()
cv2.destroyAllWindows()

