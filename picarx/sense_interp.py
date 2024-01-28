import time
import numpy as np
import logging
import atexit

try:
    from robot_hat import ADC
except ImportError:
    from sim_robot_hat import ADC


class Sensing(object):
    """Class to get sensor data from Grayscale module on PiCar-X"""

    GRAYSCALE_PINS = ['A0', 'A1', 'A2']

    def __init__(self):
        self.ch0, self.ch1, self.ch2 = [ADC(pin) for pin in self.GRAYSCALE_PINS]

    def get_grayscale_data(self, is_normal:bool=True):
        """Function to get the values"""

        # Read the data
        data = [self.ch0.read(), self.ch1.read(), self.ch2.read()]

        # Normalize the data
        if is_normal:
            # Normalize the data with Normal Distribution
            data = (data - np.mean(data)) / (np.std(data) + 1e-9) # Add a small value to avoid division by zero
        else:
            # Normalize the data with just mean
            data = data / (np.mean(data) + 1e-9) # Add a small value to avoid division by zero

        return data


class Interpret(object):
    """Class to interpret sensor data from Grayscale module on PiCar-X

    Args:
        l_th: Threshold for slight turn
        h_th: Threshold for hard turn
        polarity: Polarity of the line (1 for black line on white background, -1 for white line on black background)
    """

    def __init__(self, l_th:float=0.5, h_th:float=1.0, polarity:int=1):

        # Set the thresholds
        self.l_th = l_th
        self.h_th = h_th

        # Set the polarity
        self.polarity = polarity

        # Intialize the sensing module
        self.sensor = Sensing()

    def get_direction(self):
        """Function to get direction and degree of turn based on sensor data"""

        # Get the sensor data
        data = self.sensor.get_grayscale_data() # (3x1)

        # Take difference between sensor data to get edge
        edge = np.diff(data) # (2x1)
        edge[1] *= -1 # To get edge values of extreme sensors wrt to center sensor
        edge_val = np.abs(edge)
        edge_sign = np.sign(edge)

        # Get the direction of turn


if __name__ == "__main__":

    # Testing sensing module
    sensor = Sensing()

    try:
        while True:
            data= sensor.get_grayscale_data()
            print(f"Data: {data}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped by User")