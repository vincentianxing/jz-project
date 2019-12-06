import cv2
import numpy as np
import argparse

hand_hist = None # histogram generated from hand sample
size = 9 # number of rectangles
hand_rect_one_x = None
hand_rect_one_y = None
hand_rect_two_x = None
hand_rect_two_y = None
traverse_point = []

# resize ouput window
def rescale_frame(frame, wpercent=90, hpercent=90):
    width = int(frame.shape[1] * wpercent / 100)
    height = int(frame.shape[0] * hpercent / 100)
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)

# draw region for skin sample
def draw_rect(frame):
    rows, cols, _ = frame.shape
    global size, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y

    # four arrays to hold the coordinates of each rectangle
    hand_rect_one_x = np.array(
        [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 9 * rows / 20, 9 * rows / 20, 9 * rows / 20, 12 * rows / 20,
         12 * rows / 20, 12 * rows / 20], dtype=np.uint32)
    hand_rect_one_y = np.array(
        [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20,
         10 * cols / 20, 11 * cols / 20], dtype=np.uint32)
    hand_rect_two_x = hand_rect_one_x + 10
    hand_rect_two_y = hand_rect_one_y + 10

    # interates over arrays and draws rectangle on the frame
    for i in range(size):
        cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                      (hand_rect_two_y[i], hand_rect_two_x[i]),
                      (0, 255, 0), 1)
    return frame

# generate histogram for skin regions
def hand_histogram(frame):
    global hand_rect_one_x, hand_rect_one_y

    # transforms input frame to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # create an image of size 90 * 10 with 3 color channels
    roi = np.zeros([90, 10, 3], dtype=hsv.dtype)

    for i in range(size):
        roi[i * 10: i * 10 + 10, 0: 10] = hsv[hand_rect_one_x[i]:hand_rect_one_x[i] + 10,
                                                    hand_rect_one_y[i]:hand_rect_one_y[i] + 10]
    
    # create a histogram using the roi matrix for the skin color
    hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])
    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)

# find components of the frame that contains skin with back projection
def hist_masking(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # apply back projection useing a histogram to separate features in an image
    dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)

    # smoothen the image
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
    cv2.filter2D(dst, -1, disc, dst)
    ret, thresh = cv2.threshold(dst, 100, 255, 0)

    thresh = cv2.merge((thresh, thresh, thresh))
    cv2.GaussianBlur(dst, (3, 3), 0, dst)

    # mask the input frame
    res = cv2.bitwise_and(frame, thresh)
    return res

# find all the contours of regions of skin color
def contours(hist_mask_image):
    gray = cv2.cvtColor(hist_mask_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 0, 255, 0)
    # return a tree structure of contours
    cont, hierarchy = cv2.findContours(
        thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cont

# find the contours with max area
def max_contour(contour_list, frame):
    max_i = 0
    max_area = 0

    for i in range(len(contour_list)):
        cnt = contour_list[i]
        area = cv2.contourArea(cnt)
        if area > max_area:
            max_area = area
            max_i = i

    return contour_list[max_i], max_i

# calculate the centroid of max_contour
def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return (cx, cy)
    else:
        return None

# find the farthest point from centroid
def farthest_point(defects, contour, centroid):
    if defects is not None and centroid is not None:
        s = defects[:, 0][:, 0]
        cx, cy = centroid

        x = np.array(contour[s][:, 0][:, 0], dtype=np.float)
        y = np.array(contour[s][:, 0][:, 1], dtype=np.float)

        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None

def manipulate(frame, hand_hist):
    # mask image with skin hsv
    hist_mask_image = hist_masking(frame, hand_hist)
    # find all contours
    contour_list = contours(hist_mask_image)
    # find max contour
    max_cont, max_cont_i = max_contour(contour_list, frame)
    cv2.drawContours(frame, contour_list, max_cont_i, [0, 0, 255], 4)

    # convert contour to 2d coordinates
    c = np.array(max_cont).squeeze()
    #x = c.squeeze()[:, 0]
    #y = c.squeeze()[:, 1]

    for value in np.ndenumerate(c):
        x = value[0][0]
        y = value[1]

    for c in max_cont:
        M = cv2.moments(c)
        if M['m00'] != 0:
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])
            cv2.circle(frame, (cx, cy), 5, [255, 0, 0], -1)

    cnt_centroid = centroid(max_cont)
    cv2.circle(frame, cnt_centroid, 5, [255, 0, 255], -1)
    return frame, max_cont

def main():
    global hand_hist
    is_hand_hist_created = False
    capture = cv2.VideoCapture(0)
    # generate background subtraction mask
    backsub = cv2.createBackgroundSubtractorMOG2()

    while capture.isOpened():
        pressed_key = cv2.waitKey(1)

        # read a frame from webcam
        ret, frame = capture.read()

        # background subtraction
        fgmask = backsub.apply(frame)
        rgbmask = cv2.cvtColor(fgmask, cv2.COLOR_GRAY2BGR)
        rgbframe = frame & rgbmask

        # press 'z' to take sample
        if pressed_key & 0xFF == ord('z'):
            is_hand_hist_created = True
            hand_hist = hand_histogram(frame)

        if is_hand_hist_created:
            frame = manipulate(frame, hand_hist)[0]
            # tracking with background removed
            # frame = manipulate(rgbframe, hand_hist)[0]

        else:
            frame = draw_rect(frame)

        cv2.imshow("webcam", rescale_frame(frame))

        if pressed_key == 27:
            break

    cv2.destroyAllWindows()
    capture.release()

if __name__ == '__main__':
    main()
