import time
from sense_interp import Interpret
from utils import Bus


class LineFollowControl(object):
    """Simple class to return control angle for line following"""

    def __init__(self, scale:float=30.0):
        """Initialize the class

        Args:
            scale: Scaling factor for the control angle
        """

        # Set the scale
        self.scale = scale

        # Initialize the bus
        self.control_bus = Bus()

    def get_control_angle(self, direction):
        """Function to get the control angle"""

        # Get the control angle
        control_angle = direction * self.scale

        return control_angle

    def consumer_producer(self, interpret_bus:Bus):
        """Function to read interpret bus and write control bus"""

        # Get the direction
        direction = interpret_bus.read()

        # Get the control angle
        control_angle = self.get_control_angle(direction)

        # Write the control angle to bus
        self.control_bus.write(control_angle)

        return True


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