import os
import argparse
import cv2

# initialize the list of reference points and boolean indicating
# whether cropping is being performed or not
refPt = []
cropping = False

def click_and_crop(event, x, y, flags, param):
    # grab references to the global variables
    global refPt, cropping

    # if the left mouse button was clicked, record the starting
    # (x, y) coordinates and indicate that cropping is being
    # performed
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt = [(x, y)]
        cropping = True

    # check to see if the left mouse button was released
    elif event == cv2.EVENT_LBUTTONUP:
        # record the ending (x, y) coordinates and indicate that
        # the cropping operation is finished
        refPt.append((x, y))
        cropping = False

        # draw a rectangle around the region of interest
        cv2.rectangle(current_image, refPt[0], refPt[1], (0, 255, 0), 2)
        cv2.imshow("image", current_image)


ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dir", help="path to image files")
args = ap.parse_args()

cv2.namedWindow("image")
cv2.setMouseCallback("image", click_and_crop)

output_dir = args.dir + '../output'

try:
    os.makedirs(output_dir)
except OSError:
    pass

for current_file in os.listdir(args.dir):
    successful = False
    while not successful:
        current_image = cv2.imread( args.dir + current_file, cv2.IMREAD_COLOR)
        clone = current_image.copy()
        cv2.imshow("image", current_image)
        cv2.waitKey(0)
        if len(refPt) == 2:
            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            cv2.imshow("ROI", roi)
            key = cv2.waitKey(0)
            if (key == ord('s') or key == ord('k')):
                #s == save k == sKip
                if(key == ord('s')):
                    cv2.imwrite(output_dir + "/" + current_file, roi)
                os.remove(args.dir + current_file)
                successful = True
            if key == ord('q'):
                cv2.destroyAllWindows()
                quit()

            cv2.destroyWindow("ROI")


#input_files = os.listdir(args.dir)
#current_image = cv2.imread( args.dir + input_files[0], cv2.IMREAD_COLOR)
#clone = current_image.copy()

#cv2.imshow("image", current_image)
#key = cv2.waitKey(0)

#if len(refPt) == 2:
#    roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
#    cv2.imshow("ROI", roi)
#    key = cv2.waitKey(0)
#    if key == ord('s'):
#        cv2.imwrite( output_dir + "/" + input_files[0], roi)


#input_files = os.listdir(args.dir)
#for current_file in os.listdir(args.dir):
#    current_image = cv2.imread( args.dir + current_file, cv2.IMREAD_COLOR)
#    cv2.imshow('test', current_image)
#    key = cv2.waitKey(0)
#    if key == ord('q'):
#        break