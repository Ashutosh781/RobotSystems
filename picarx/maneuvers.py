import time
from picarx_improved import Picarx


class Maneuvers(Picarx):
    '''Class for performing maneuvers with the PiCar-X'''

    # Constants for safe speed and angle for maneuvers
    SAFE_SPEED = 30
    SAFE_ANGLE = 20

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
        '''Drive forward or backward with a given speed and angle

        Args:
            speed: ratio [-100, 100] (negative for backward)
            angle: degrees [-30, 30] (negative for left)
        '''

        # Call the appropriate function based on the speed
        if speed >= 0:
            self.forward_with_angle(abs(speed), angle)
        else:
            self.backward_with_angle(abs(speed), angle)

    def parallel_park(self, park_to='l'):
        '''Parallel park in either direction

        Args:
            park_to: 'l' or 'r' (default 'l')
        '''

        # Set the direction of parking
        if park_to == 'l':
            direction = -1
        elif park_to == 'r':
            direction = 1

        # Drive forward
        self.drive_steer(self.SAFE_SPEED, 0)
        time.sleep(1)

        # Drive backward and turn into the parking spot
        self.drive_steer(-self.SAFE_SPEED, direction * self.SAFE_ANGLE)
        time.sleep(2)

        # Drive backward and straighten the heading
        self.drive_steer(-self.SAFE_SPEED, -direction * self.SAFE_ANGLE)
        time.sleep(2)

        # Straighten the wheels
        self.drive_steer(-self.SAFE_SPEED, 0)
        time.sleep(0.25)

        # Stop
        self.stop()

    def three_point_turn(self, turn_to='l'):
        '''Three point turn in either direction

        Args:
            turn_to: 'l' or 'r' (default 'l')
        '''

        # Set the direction of turning
        if turn_to == 'l':
            direction = -1
        elif turn_to == 'r':
            direction = 1

        # Drive forward and turn to direction
        self.drive_steer(self.SAFE_SPEED, direction * self.SAFE_ANGLE)
        time.sleep(4)

        # Drive backward and turn to opposite direction
        self.drive_steer(-self.SAFE_SPEED, -direction * self.SAFE_ANGLE)
        time.sleep(4.5)

        # Drive forward and straight
        self.drive_steer(self.SAFE_SPEED, 0)
        time.sleep(4)

        # Stop
        self.stop()


if __name__ == '__main__':

    # Variables for testing
    speed = 50 # ratio [-100, 100]
    angle = 15 # degrees [-30, 30]
    park_to = 'r' # 'l' or 'r'
    turn_to = 'l' # 'l' or 'r'

    # Create an instance of the Maneuvers class
    skills = Maneuvers()

    # Test the drive_steer() function
    skills.drive_steer(speed, angle)
    time.sleep(2)
    skills.stop()

    # Test the parallel_park() function
    skills.parallel_park(park_to)

    # Test the three_point_turn() function
    skills.three_point_turn(turn_to)
