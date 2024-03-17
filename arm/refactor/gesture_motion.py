#!/usr/bin/python3
# coding=utf8

from time import sleep

# Imports from existing ArmPi code
import sys
sys.path.append('/home/pi/ArmPi/')
from ArmIK.ArmMoveIK import ArmIK
import HiwonderSDK.Board as Board


class GestureMotion():
    """Class to move the arm based on detected gestures."""

    def __init__(self):

        # Arm instance
        self.arm = ArmIK()
        # Home position
        self.home_position()

    def home_position(self):
        """Move the arm to the home position"""

        Board.setBusServoPulse(1, 500, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.arm.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)
        sleep(1)

    def motion_gesture(self, gesture:int):
        """Move arm based on gesture. Right now only basic motion defined."""

        if gesture == 0:
            # Move first motor
            sleep(0.5)
            Board.setBusServoPulse(1, 100, 300)
            sleep(0.5)
            Board.setBusServoPulse(1, 500, 300)
            sleep(0.5)
        elif gesture == 1:
            # Move second motor
            sleep(0.5)
            Board.setBusServoPulse(2, 300, 300)
            sleep(0.5)
            Board.setBusServoPulse(2, 800, 300)
            sleep(0.5)
            Board.setBusServoPulse(2, 500, 300)
            sleep(0.5)
        elif gesture == 2:
            # Move third motor
            sleep(0.5)
            Board.setBusServoPulse(3, 500, 300)
            sleep(0.5)
            Board.setBusServoPulse(3, 200, 300)
            sleep(0.5)
        elif gesture == 3:
            # Move fourth motor
            sleep(0.5)
            Board.setBusServoPulse(4, 600, 300)
            sleep(0.5)
            Board.setBusServoPulse(4, 800, 300)
            sleep(0.5)
        elif gesture == 4:
            # Move fifth motor
            sleep(0.5)
            Board.setBusServoPulse(5, 600, 300)
            sleep(0.5)
            Board.setBusServoPulse(5, 800, 300)
            sleep(0.5)
        else:
            pass


if __name__ == '__main__':

    # Motion object
    gm = GestureMotion()

    # Test parameters
    gesture = 5

    # Test motion
    gm.motion_gesture(gesture=gesture)