import time
from picarx_improved import PicarX


class Maneuvers(PicarX):
    '''Class for performing maneuvers with the PiCar-X'''

    def __init__(self):
        super().__init__()

    def forward_with_angle(self, speed, angle):
        '''Drive forward with a given speed and angle'''

        # Set the direction servo angle
        self.dir_servo_pin.angle(angle)

        # Use forward() to drive forward with ackerman steering
        self.forward(speed, is_ackerman=True)

    def backward_with_angle(self, speed, angle):
        '''Drive backward with a given speed and angle'''

        # Set the direction servo angle
        self.dir_servo_pin.angle(angle)

        # Use backward() to drive backward with ackerman steering
        self.backward(speed, is_ackerman=True)


if __name__ == '__main__':

    # Variables for testing
    speed = 50 # ratio of 0-100
    angle = 0 # degrees

    # Test the Maneuvers class
    skills = Maneuvers()
    skills.forward_with_angle(speed, angle)
    time.sleep(1)
    skills.stop()