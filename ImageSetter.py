import os
import argparse
import cv2
import json
import io
import os

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
json_path = args.dir + 'crops.json'

if os.path.isfile(json_path) and os.access(json_path, os.R_OK):
    crop_info = json.load(open(json_path))
else:
    io.open(os.path.join(args.dir, 'crops.json'), 'w')
    crop_info = {}

try:
    os.makedirs(output_dir)
except OSError:
    pass

for current_file in os.listdir(args.dir):
    successful = False

    if current_file in crop_info:
        continue

    while not successful:
        current_image = cv2.imread( args.dir + current_file, cv2.IMREAD_COLOR)
        clone = current_image.copy()
        cv2.imshow("image", current_image)
        cv2.waitKey(0)
        if len(refPt) == 2:
            top_x = refPt[0][1]
            top_y = refPt[1][1]
            bot_x = refPt[0][0]
            bot_y = refPt[1][0]
            roi = clone[refPt[0][1]:refPt[1][1], refPt[0][0]:refPt[1][0]]
            cv2.imshow("ROI", roi)
            key = cv2.waitKey(0)
            file_data = {}
            if (key == ord('s') or key == ord('k')):
                #s == save k == sKip
                if(key == ord('s')):
                    cv2.imwrite(output_dir + "/" + current_file, roi)
                    file_data["top_x"] = top_x
                    file_data["top_y"] = top_y
                    file_data["bot_x"] = bot_x
                    file_data["bot_y"] = bot_y
                    file_data["skipped"] = False
                if (key == ord('k')):
                    file_data["skipped"] = True
                successful = True
                crop_info[current_file] = file_data
            if key == ord('q'):
                with open(json_path, 'w') as outfile:
                    json.dump(crop_info, outfile)
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