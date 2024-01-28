import time
import numpy as np
import logging
import atexit

try:
    from robot_hat import ADC, Grayscale_Module
except ImportError:
    from sim_robot_hat import ADC, Grayscale_Module


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
            data = (data - np.mean(data)) / np.std(data)
        else:
            # Normalize the data with just mean
            data = data / np.mean(data)

        return data


class Interpret(Sensing):
    """Class to interpret sensor data from Grayscale module on PiCar-X"""

    def __init__(self):
        super().__init__()

    def interpret_grayscale(self):
        """Function to interpret the values"""

        pass


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