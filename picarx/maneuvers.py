import time
from picarx_improved import Picarx


class Maneuvers(Picarx):
    '''Class for performing maneuvers with the PiCar-X'''

    def __init__(self):
        super().__init__()

        # Set the direction servo to the center position
        self.set_dir_servo_angle(0)

    def forward_with_angle(self, speed, angle):
        '''Drive forward with a given speed and angle'''

        # Set the direction servo angle
        self.set_dir_servo_angle(angle)

        # Use forward() to drive forward with ackerman steering
        self.forward(speed, is_ackerman=True)

    def backward_with_angle(self, speed, angle):
        '''Drive backward with a given speed and angle'''

        # Set the direction servo angle
        self.set_dir_servo_angle(angle)

        # Use backward() to drive backward with ackerman steering
        self.backward(speed, is_ackerman=True)

    def drive_steer(self, speed, angle):
        '''Drive forward or backward with a given speed and angle'''

        # Call the appropriate function based on the speed
        if speed >= 0:
            self.forward_with_angle(abs(speed), angle)
        else:
            self.backward_with_angle(abs(speed), angle)

if __name__ == '__main__':

    # Variables for testing
    speed = 30 # ratio [-100, 100]
    angle = 15 # degrees [-30, 30]

    # Test the Maneuvers class
    skills = Maneuvers()
    skills.drive_steer(speed, angle)
    time.sleep(2)
    skills.stop()