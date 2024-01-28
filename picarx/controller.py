import time
from sense_interp import Interpret


class LineFollowControl(object):
    """Simple class to return control angle for line following"""

    def __init__(self, scale:float=10.0):
        """Initialize the class

        Args:
            scale: Scaling factor for the control angle
        """

        # Set the scale
        self.scale = scale

    def get_control_angle(self, direction):
        """Function to get the control angle"""

        # Get the control angle
        control_angle = direction * self.scale

        return control_angle


if __name__ == '__main__':

    # Test the class
    controller = LineFollowControl()
    interp = Interpret()

    try:
        while True:
            direction = interp.get_direction()
            angle = controller.get_control_angle(direction)
            print(f"Angle: {angle}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated!")