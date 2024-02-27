#!/usr/bin/python3
# coding=utf8

import cv2
import math
import numpy as np
from camera import Camera


class ColorTrack():
    """Color tracking class"""

    def __init__(self):

        # For color of bounding box
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }

        # Color range to detect
        self.color_range = {
            'red': [(0, 151, 100), (255, 255, 255)],
            'green': [(0, 0, 0), (255, 115, 255)],
            'blue': [(0, 0, 0), (255, 255, 110)],
            'black': [(0, 0, 0), (56, 255, 255)],
            'white': [(193, 0, 0), (255, 250, 255)],
        }

        # Possible color check
        self._possible_color = ['red', 'green', 'blue']

        # Variables
        self.get_roi = False
        self.size = (640, 480)
        self.roi = ()
        self.image_center_distance = 20
        self.square_length = 3

        # Target colors
        self._target_color = []

        # Parameters from the camera calibration
        self.map_param_path = '/home/pi/ArmPi/CameraCalibration/map_param.npz'
        self.param_data = np.load(self.map_param_path)
        self.map_param_ = self.param_data['map_param']

    def setTargetColor(self, target_color:list):
        """Set detection color"""

        # Check if the color is valid
        target_color = [i for i in target_color if i in self._possible_color]
        self._target_color = target_color

        return True

    def getAreaMaxContour(self, contours):
        """Find contour with the largest area
        Args:
            contours: Contour list to compare
        """

        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None

        for c in contours:
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:
                    area_max_contour = c

        return area_max_contour, contour_area_max

    def getMaskROI(self, frame, roi, size):
        x_min, x_max, y_min, y_max = roi
        x_min -= 10
        x_max += 10
        y_min -= 10
        y_max += 10

        if x_min < 0:
            x_min = 0
        if x_max > size[0]:
            x_max = size[0]
        if y_min < 0:
            y_min = 0
        if y_max > size[1]:
            y_max = size[1]

        black_img = np.zeros([size[1], size[0]], dtype=np.uint8)
        black_img = cv2.cvtColor(black_img, cv2.COLOR_GRAY2RGB)
        black_img[y_min:y_max, x_min:x_max] = frame[y_min:y_max, x_min:x_max]

        return black_img

    def getROI(self, box):
        x_min = min(box[0, 0], box[1, 0], box[2, 0], box[3, 0])
        x_max = max(box[0, 0], box[1, 0], box[2, 0], box[3, 0])
        y_min = min(box[0, 1], box[1, 1], box[2, 1], box[3, 1])
        y_max = max(box[0, 1], box[1, 1], box[2, 1], box[3, 1])

        return (x_min, x_max, y_min, y_max)

    def leMap(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def world2pixel(self, l, size):
        l_ = round(l/self.map_param_, 2)
        l_ = self.leMap(l_, 0, 640, 0, size[0])

        return l_

    def convertCoordinate(self, x, y, size):
        x = self.leMap(x, 0, size[0], 0, 640)
        x = x - 320
        x_ = round(x * self.map_param_, 2)

        y = self.leMap(y, 0, size[1], 0, 480)
        y = 240 - y
        y_ = round(y * self.map_param_ + self.image_center_distance, 2)

        return x_, y_

    def getCenter(self, rect, roi, size, square_length):
        x_min, x_max, y_min, y_max = roi
        # Select vertex closest to the center of the image based on the center of the object
        if rect[0][0] >= size[0]/2:
            x = x_max
        else:
            x = x_min
        if rect[0][1] >= size[1]/2:
            y = y_max
        else:
            y = y_min

        # Calculate diagonal length
        square_l = square_length/math.cos(math.pi/4)

        # Convert length to pixel length
        square_l = self.world2pixel(square_l, size)

        # Calculate center based on rotation angle of the object
        dx = abs(math.cos(math.radians(45 - abs(rect[2]))))
        dy = abs(math.sin(math.radians(45 + abs(rect[2]))))

        if rect[0][0] >= size[0] / 2:
            x = round(x - (square_l/2) * dx, 2)
        else:
            x = round(x + (square_l/2) * dx, 2)
        if rect[0][1] >= size[1] / 2:
            y = round(y - (square_l/2) * dy, 2)
        else:
            y = round(y + (square_l/2) * dy, 2)

        return  x, y

    def run(self, img):
        """Run the color tracking module
        Args:
            img: Image to process
        """

        img_copy = img.copy()
        img_h, img_w = img.shape[:2]
        cv2.line(img, (0, int(img_h / 2)), (img_w, int(img_h / 2)), (0, 0, 200), 1)
        cv2.line(img, (int(img_w / 2), 0), (int(img_w / 2), img_h), (0, 0, 200), 1)

        frame_resize = cv2.resize(img_copy, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)

        # This forces only one object to be detected at a time
        if self.get_roi:
            self.get_roi = False
            frame_gb = self.getMaskROI(frame_gb, self.roi, self.size)

        # Convert image to LAB color space
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)

        area_max = 0
        areaMaxContour = 0

        if len(self._target_color) == 0:
            # If no color is set, detect all possible colors
            self._target_color = self._possible_color

        for i in self._target_color:
            # Mask the image
            frame_mask = cv2.inRange(frame_lab, self.color_range[i][0], self.color_range[i][1])
            # Opening and closing operations to remove noise
            opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
            # Find contours
            contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
            # Find the contour with the largest area
            areaMaxContour, area_max = self.getAreaMaxContour(contours)

            if area_max > 2500:
                rect = cv2.minAreaRect(areaMaxContour)
                box = np.int0(cv2.boxPoints(rect))

                # Get ROI
                self.roi = self.getROI(box)
                # self.get_roi = True

                # Get the center of the object
                img_centerx, img_centery = self.getCenter(rect, self.roi, self.size, self.square_length)
                # Convert the center of the object to the world coordinate
                world_x, world_y = self.convertCoordinate(img_centerx, img_centery, self.size)

                cv2.drawContours(img, [box], -1, self.range_rgb[i], 2)
                # Draw the center of the object
                cv2.putText(img, '(' + str(world_x) + ',' + str(world_y) + ')', (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[i], 1)

        return img


if __name__ == '__main__':

    # Color tracking module
    ct = ColorTrack()

    # Set the target color
    target_color = ct._possible_color
    ct.setTargetColor(target_color)

    # Camera instance
    cam = Camera()
    cam.camera_open()

    while True:
        img = cam.frame
        if img is not None:
            frame = img.copy()
            Frame = ct.run(frame)

            cv2.imshow('Frame', Frame)
            key = cv2.waitKey(1)

            if key == 27:
                # Press 'ESC' to exit
                break

    cam.camera_close()
    cv2.destroyAllWindows()