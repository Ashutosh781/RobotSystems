import time
import atexit
from controller import LineFollowControl
from sense_interp import Interpret
from maneuvers import Maneuvers


class LineFollower(Maneuvers):
    """Class to implement line following

    Args:
        scale: Scaling factor for the control angle
        l_th: Threshold for slight turn
        h_th: Threshold for hard turn
        polarity: Polarity of the line (-1 for black line on white background, 1 for white line on black background)
        is_normal: Normalize the data with Normal Distribution or just divide by mean
    """

    def __init__(self, scale:float=10.0, l_th:float=0.35, h_th:float=0.8, polarity:int=-1, is_normal:bool=False):

        # Initialize the parent class
        super().__init__()

        # Set the scale
        self.scale = scale

        # Set the thresholds
        self.l_th = l_th
        self.h_th = h_th

        # Set the polarity
        self.polarity = polarity
        self.is_normal = is_normal

        # Initialize the controller
        self.controller = LineFollowControl(scale=self.scale)

        # Initialize the sensor interpreter
        self.interpreter = Interpret(l_th=self.l_th, h_th=self.h_th, polarity=self.polarity, is_normal=self.is_normal)
        time.sleep(0.5)

        # Atexit register again for safety
        atexit.register(self.stop)

    def follow_line(self):
        """Function to follow the line"""

        # Get the direction
        direction = self.interpreter.get_direction()

        # Get the control angle
        angle = self.controller.get_control_angle(direction)

        print(f"Angle: {angle}")

        # Drive forward with the control angle
        self.forward_with_angle(self.SAFE_SPEED, angle)

    def main(self):
        """Main function"""

        try:
            while True:
                self.follow_line()
                time.sleep(0.01)

        except KeyboardInterrupt:
            self.stop()
            self.set_dir_servo_angle(0.0)
            print("Stopped")


if __name__ == "__main__":

    # Parameters
    scale = 10.0
    l_th = 0.35
    h_th = 0.8
    polarity = -1
    is_normal = False

    lf = LineFollower(scale, l_th, h_th, polarity, is_normal)
    lf.main()