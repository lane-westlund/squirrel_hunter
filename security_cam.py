import numpy as np
import cv2
import argparse
import time
import imutils
import datetime
import os

ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to video")
ap.add_argument("-a", "--min-area", type=int, default=(500), help="minimum")
args = vars(ap.parse_args())

#no video arg = webcam
if args.get("video", None) is None:
    camera = cv2.VideoCapture(0)
    time.sleep(0.25)
#otherwise, read from video file
else:
    camera= cv2.VideoCapture(args["video"])

#fgbg = cv2.bgsegm.createBackgroundSubtractorGMG()
#fgbg = cv2.bgsegm.createBackgroundSubtractorCNT()
fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

frame_list = list()
movement_detected = False

try:
    os.makedirs('output_dir')
except OSError:
    pass

while True:

    (grabbed, frame_orrig) = camera.read()

    # if we didn't read
    if not grabbed:
        break;


    frame_list.append(frame_orrig)
    if len(frame_list) == 120:
        frame_list.pop(0)

    #sizing stuff
    frame = imutils.resize(frame_orrig, width=(500))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21,21), 0)

    fgmask = fgbg.apply(frame)

    thresh = cv2.threshold(fgmask, 25, 255, cv2.THRESH_BINARY)[1]
    #dilate the threshold image to fill in holes, then find contours
    #on the threshold image
    thresh = cv2.dilate(thresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #loop over the contours
    movement_detected = False

    for c in cnts:
        if cv2.contourArea(c) < args["min_area"]:
            continue

        (x, y, w, h) = cv2.boundingRect(c)
        movement_detected = True
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0, 255, 0), 2 )

    cv2.imshow('mask', fgmask)
    cv2.imshow('frame', frame)
    if(movement_detected == True):
        cv2.imshow('last', frame_list[0])
        dt = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        cv2.imwrite('output_dir/'+dt+'_hint.png', frame)
        cv2.imwrite('output_dir/'+dt+'_full.png', frame_orrig)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()

