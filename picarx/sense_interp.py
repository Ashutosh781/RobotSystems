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
        time.sleep(0.5)

        # Maybe need to calibrate the sensors at startup

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
        polarity: Polarity of the line (-1 for black line on white background, 1 for white line on black background)
        is_normal: Normalize the data with Normal Distribution or just divide by mean
    """

    def __init__(self, l_th:float=0.35, h_th:float=0.8, polarity:int=-1, is_normal:bool=False):

        # Set the thresholds
        self.l_th = l_th
        self.h_th = h_th

        # Set the polarity
        self.polarity = polarity
        self.is_normal = is_normal

        # Intialize the sensing module
        self.sensor = Sensing()

        # Just for record tracking
        self.prev_direction = 0.0

    def get_direction(self):
        """Function to get direction and degree of turn based on sensor data"""

        # Get the sensor data
        data = self.sensor.get_grayscale_data(is_normal=self.is_normal) # (3x1)

        # Take difference between sensor data to get edge
        edge = np.diff(data) # (2x1)
        edge[1] *= -1 # To get edge values of extreme sensors wrt to center sensor
        edge_val = np.abs(edge)
        edge_sign = np.sign(edge)

        ''' Logic for getting turn direction
        1. If edge values are above h_th for both sensors, edge signs are same as polarity, then zero turn - denoted by 0
        2. If edge[0] is lower than l_th and edge[1] is not, edge[1] is same as polarity, then slight left - denoted by -0.5
        3. If edge[0] is higher than l_th and edge[1] is not, edge[0] is opposite of polarity, then sharp left - denoted by -1
        4. If edge[1] is lower than l_th and edge[0] is not, edge[0] is same as polarity, then slight right - denoted by 0.5
        5. If edge[1] is higher than l_th and edge[0] is not, edge[1] is opposite of polarity, then sharp right - denoted by 1
        6. If none of the above conditions are satisfied, then just return the previous direction. This is to avoid sudden changes in direction and a design choice.
        '''

        ## Get the turn direction
        # Straight
        if edge_val[0] >= self.h_th and edge_val[1] >= self.h_th and edge_sign[0] == edge_sign[1] == self.polarity:
            direction = 0.0
        # Slight left
        elif edge_val[0] <= self.l_th and edge_val[1] >= self.l_th and edge_sign[1] == self.polarity:
            direction = -0.5
        # Sharp left
        elif edge_val[0] >= self.h_th and edge_val[1] <= self.l_th and edge_sign[0] == -self.polarity:
            direction = -1.0
        # Slight right
        elif edge_val[0] >= self.l_th and edge_val[1] <= self.l_th and edge_sign[0] == self.polarity:
            direction = 0.5
        # Sharp right
        elif edge_val[0] <= self.l_th and edge_val[1] >= self.h_th and edge_sign[1] == -self.polarity:
            direction = 1.0
        # Unknown
        else:
            direction = self.prev_direction

        # Update the previous direction
        self.prev_direction = direction

        return direction

if __name__ == "__main__":

    # Testing interpretation module
    # Thresholds and polarity
    l_th = 0.35
    h_th = 0.8
    polarity = -1 # Black line on white background

    # Initialize the interpreter
    interpreter = Interpret(l_th=l_th, h_th=h_th, polarity=polarity)

    try:
        while True:
            direction = interpreter.get_direction()
            print(f"Direction: {direction}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program stopped by User")