import numpy as np
import cv2
import time


def getAvailableCameraIds(max_to_test):
    available_ids = []
    for i in range(max_to_test):
        temp_camera = cv2.VideoCapture(i)
        if temp_camera.isOpened():
            temp_camera.release()
            print ("found camera with id: " + format(i))
            available_ids.append(i)
    return available_ids


def displayCameraFeed(cameraId, width, height):
    cap = cv2.VideoCapture(cameraId)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while(True):
        start = time.time()
        ret, frame = cap.read()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cv2.imshow('frame',frame)
        end = time.time()
        print ("time to read a frame: " + format(end-start))

        #DISABLED
        #cv2.imshow('frame', frame)
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #break

    cap.release()
    cv2.destroyAllWindows()


#print getAvailableCameraIds(100)
displayCameraFeed(0, 640, 480)
