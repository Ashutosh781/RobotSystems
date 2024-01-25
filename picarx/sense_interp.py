import time
import numpy as np
from picarx_improved import Picarx


class Sensing(Picarx):
    """Class to get sensor data from Grayscale module on PiCar-X"""

    def __init__(self):
        super().__init__()

    def get_grayscale(self):
        """Function to get the values"""

        data = self.get_grayscale_data()
        print(f"Current data {data}")


class Interpret(Sensing):
    """Class to interpret sensor data from Grayscale module on PiCar-X"""

    def __init__(self):
        super().__init__()

    def interpret_grayscale(self):
        """Function to interpret the values"""

        pass


if __name__ == "__main__":

    sense = Sensing()
    sense.get_grayscale()