import time
import logging
import numpy as np
import rossros as rr

from utils import Bus

try:
    from robot_hat import ADC, Ultrasonic, Pin
except ImportError:
    from sim_robot_hat import ADC, Ultrasonic, Pin

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)


class Sensing(object):
    """Class to get sensor data from Grayscale module on PiCar-X"""

    GRAYSCALE_PINS = ['A0', 'A1', 'A2']

    def __init__(self):
        self.ch0, self.ch1, self.ch2 = [ADC(pin) for pin in self.GRAYSCALE_PINS]
        time.sleep(0.5)

        # Maybe need to calibrate the sensors at startup

    def get_grayscale_data(self, is_normal:bool=False):
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

    def producer(self, sensor_bus:Bus, delay:float=0.1):
        """Function to write data to bus"""

        while True:
            # Get the sensor data
            data = self.get_grayscale_data(is_normal=False)
            sensor_bus.write(data)
            # logging.info(f"Sensor: {data}")
            time.sleep(delay)


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

        # Previous direction
        self.prev_direction = 0.0

    def get_direction(self, data=None):
        """Function to get direction and degree of turn based on sensor data"""

        # Get the sensor data
        if data is None:
            # Read the data from sensor
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
        6. If none of the above conditions are satisfied, then just return previous direction, as no change in direction
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

    def consumer_producer(self, sensor_bus:Bus, interpret_bus:Bus, delay:float=0.1):
        """Function to read data from sensor bus and write interpreted data to bus"""

        while True:
            # Get the direction
            sensor_val = sensor_bus.read()
            direction = self.get_direction(data=sensor_val)
            interpret_bus.write(direction)
            # logging.info(f"Interpret: {direction}")
            time.sleep(delay)


class SenseUltra(object):
    """Class to get sensor data from Ultrasonic module on PiCar-X"""

    ULTRASONIC_PINS = ['D2', 'D3']

    def __init__(self):
        tring_pin, echo_pin = self.ULTRASONIC_PINS
        self.sensor = Ultrasonic(tring_pin, echo_pin)
        time.sleep(0.5)

    def get_ultrasonic_data(self):
        """Function to get the distance from the ultrasonic sensor"""

        # Read the data
        distance = self.sensor.read()

        return distance

    def producer(self, sensor_bus:Bus, delay:float=0.1):
        """Function to write data to bus"""

        while True:
            # Get the sensor data
            data = self.get_ultrasonic_data()
            sensor_bus.write(data)
            # logging.info(f"Sensor: {data}")
            time.sleep(delay)


class InterpretUltra(object):
    """Class to interpret sensor data from Ultrasonic module on PiCar-X"""

    def __init__(self, threshold:float=0.3):

        self.threshold = threshold

        # Intialize the sensing module
        self.sensor = SenseUltra()

    def get_obstacle(self, data=None):
        """Function to get if obstacle is detected based on sensor data"""

        # Get the sensor data
        if data is None:
            # Read the data from sensor
            data = self.sensor.get_ultrasonic_data()

        # Check if obstacle is detected
        if data <= self.threshold:
            obstacle = True
        else:
            obstacle = False

        return obstacle

    def consumer_producer(self, sensor_bus:Bus, interpret_bus:Bus, delay:float=0.1):
        """Function to read data from sensor bus and write interpreted data to bus"""

        while True:
            # Get the direction
            sensor_val = sensor_bus.read()
            obstacle = self.get_obstacle(data=sensor_val)
            interpret_bus.write(obstacle)
            # logging.info(f"Interpret: {obstacle}")
            time.sleep(delay)


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