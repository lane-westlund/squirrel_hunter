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
from CameraStream import CameraStream
import json


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
args = vars(ap.parse_args())

conf = json.load(open("conf.json"))

cam = CameraStream(resolution=tuple(conf["resolution"])).start()
time.sleep(2.0)

#fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
#fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

movement_detected = False

if conf["save_capture_files"]:
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

    frame_orrig = cam.read()

    if( datetime.datetime.now().hour < conf["start_hour"]):
        continue
    elif( datetime.datetime.now().hour >= conf["stop_hour"]):
        continue

    #sizing stuff
    frame = imutils.resize(frame_orrig, width=(conf["resize_width"]))

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
    biggest_area = 0
    height, width, channels = frame.shape
    for c in cnts:
        if cv2.contourArea(c) < (conf["movement_ratio_min"]*height*width):
            continue
        if cv2.contourArea(c) > (conf["movement_ratio_max"] * height * width):
            continue
        if cv2.contourArea(c) > biggest_area:
                biggest_area = cv2.contourArea(c)
        (x, y, w, h) = cv2.boundingRect(c)
        movement_detected = True
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2 )


    if movement_detected:
        biggest_ratio = (float(biggest_area) / (height * width))
        cv2.putText(frame, "biggest:" + str(biggest_area) + " R: " + str(biggest_ratio), (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    if conf["show_video"]:
        cv2.imshow('frame', frame)
    if conf["show_motion_mask"]:
        cv2.imshow('mask', fgmask)
    if((movement_detected == True) and (conf["save_capture_files"])):
        dt = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
        cv2.imwrite('output_dir/'+dt+'_hint.png', frame)
        cv2.imwrite('output_dir/'+dt+'_full.png', frame_orrig)
        frame_writes = frame_writes + 1
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

cam.stop()
cv2.destroyAllWindows()

