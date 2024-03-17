#!/usr/bin/python3
# coding=utf8

import cv2
import math

from collections import deque, Counter

from gesture_motion import GestureMotion

# Imports from existing ArmPi code
import sys
sys.path.append('/home/pi/ArmPi/')
from Camera import Camera


class GestureDetect:
    """Class for detecting gestures from camera feed using OpenCV."""

    def __init__(self):
        # Camera instance
        self.cam = Camera()
        self.cam.camera_open()

        # Gesture motion instance
        self.gm = GestureMotion()

        # Queue
        # fps = 30, so 60 frames = 2 seconds
        self.window = 60
        self.dq = deque(maxlen=self.window)

    def preprocess(self, img):
        """Pre process the roi image before contour detection"""

        # Convert the ROI to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Gaussian blur to reduce noise
        blur = cv2.GaussianBlur(gray, (35, 35), 0)
        # Threshold the image
        _, threshold = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        return threshold

    def itr_defects(self, defects, cnt):
        """Iterate through defects and draw lines and circles on the image."""

        count = 0

        for i in range(defects.shape[0]):
            s, e, f, _ = defects[i, 0]
            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])

            # Get angle of each defect
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            # If angle is less than 90, count it as a finger
            if angle <= 90:
                count += 1

        return count

    def detect_gesture(self, img):
        """Detects gestures from camera feed."""

        # Preprocess the image
        roi = self.preprocess(img)

        # Find contours
        contours, _ = cv2.findContours(roi.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # Get the contour with the maximum area
        cnt = max(contours, key=lambda x: cv2.contourArea(x))
        # Convex hull
        hull = cv2.convexHull(cnt)

        # Draw contours
        cv2.drawContours(img, [cnt], 0, (255, 0, 0), 2)

        # Convexity defects
        hull = cv2.convexHull(cnt, returnPoints=False)
        defects = cv2.convexityDefects(cnt, hull)
        defect_count = None

        # Iterate through defects
        if defects is not None:
            defect_count = self.itr_defects(defects, cnt)

        # Put image text for number of fingers
        font = cv2.FONT_HERSHEY_SIMPLEX
        colour = (0, 0, 255)
        if defect_count == 0:
            cv2.putText(img, "One", (50, 50), font, 2, colour)
        elif defect_count == 1:
            cv2.putText(img, "Two", (50, 50), font, 2, colour)
        elif defect_count == 2:
            cv2.putText(img, "Three", (50, 50), font, 2, colour)
        elif defect_count == 3:
            cv2.putText(img, "Four", (50, 50), font, 2, colour)
        elif defect_count == 4:
            cv2.putText(img, "Five", (50, 50), font, 2, colour)
        else:
            cv2.putText(img, "None", (50, 50), font, 2, colour)

        return defect_count

    def run(self):
        """Run loop"""

        while True:
            frame = self.cam.frame
            if frame is not None:
                # Detect gestures
                defects = self.detect_gesture(frame)

                # Append to queue
                self.dq.append(defects)
                count = Counter(self.dq)

                cv2.imshow('frame', frame)
                key = cv2.waitKey(1) & 0xFF

                # Press 'q' to quit
                if key == ord('q'):
                    print("Quitting...")
                    break

                # If most common gesture is detected for 2 seconds move the arm
                if count.most_common(1)[0][1] == self.window:
                    # Get the most common gesture
                    gesture = int(count.most_common(1)[0][0])
                    # Move the arm
                    self.gm.motion_gesture(gesture=gesture)

        # Clean up
        cv2.destroyAllWindows()
        self.cam.camera_close()
        self.gm.home_position()


if __name__ == "__main__":

    # Gesture detection
    gd = GestureDetect()
    # Run the loop
    gd.run()