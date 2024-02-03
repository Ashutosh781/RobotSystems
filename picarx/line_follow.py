import time
import concurrent.futures
from utils import Bus
from controller import LineFollowControl
from sense_interp import Sensing, Interpret
from maneuvers import Maneuvers
from camera_handle import CameraHandle


class LineFollower(Maneuvers):
    """Class to implement line following using Gray Scale Sensors or Camera

    Args:
        scale: Scaling factor for the control angle
        polarity: Polarity of the line (-1 for black line on white background, 1 for white line on black background)
        l_th: Threshold for slight turn
        h_th: Threshold for hard turn
        is_normal: Normalize the data with Normal Distribution or just divide by mean
        is_camera: Use the camera for line following
        cam_thresh: Threshold for line detection using camera
    """

    def __init__(self, scale:float=30.0, polarity:int=-1, speed:int=22,
                l_th:float=0.35, h_th:float=0.8, is_normal:bool=False,
                is_camera:bool=False, cam_thresh:int=50):

        # Initialize the parent class
        super().__init__()

        # Set the scale
        self.scale = scale

        # Set the thresholds
        self.l_th = l_th
        self.h_th = h_th
        self.cam_thresh = cam_thresh

        # Set the polarity
        self.polarity = polarity

        self.speed = speed
        self.is_normal = is_normal
        self.is_camera = is_camera

        # Previous direction
        self.prev_direction = 0.0

        # Initialize the controller
        self.controller = LineFollowControl(scale=self.scale)

        # Initialize the sensor interpreter
        if not is_camera:
            self.interpreter = Interpret(l_th=self.l_th, h_th=self.h_th, polarity=self.polarity, is_normal=self.is_normal)
        else:
            self.camera = CameraHandle(polarity=self.polarity, thresh=self.cam_thresh)
        time.sleep(0.5)

    def follow_line(self, image=None):
        """Function to follow the line"""

        # Get the direction
        if not self.is_camera:
            direction = self.interpreter.get_direction()
        else:
            direction = self.camera.get_shift(image, is_draw=False)

        # If None - that means no case satisfied - then use the previous direction
        if direction is None:
            direction = self.prev_direction

        # Get the control angle
        angle = self.controller.get_control_angle(direction)

        self.prev_direction = direction

        # Drive forward with the control angle
        self.forward_with_angle(self.speed, angle)

    def consumer(self, control_bus:Bus, delay:float=0.1):
        """Function to run the robot with last controller output"""

        try:
            while True:
                # Get the control angle
                angle = control_bus.read()
                self.drive_steer(self.speed, angle)
                time.sleep(delay)

        except KeyboardInterrupt:
            self.stop()
            print("Robot stopped by User")


def lf_grayscale_main(scale:float=30.0, polarity:int=-1, speed:int=22, l_th:float=0.35, h_th:float=0.8, is_normal:bool=False):
    """Main function to follow the line using grayscale sensors"""

    lf = LineFollower(scale=scale, polarity=polarity, speed=speed, l_th=l_th, h_th=h_th, is_normal=is_normal, is_camera=False)
    try:
        while True:
            lf.follow_line()

    except KeyboardInterrupt:
        lf.stop()
        lf.set_dir_servo_angle(0.0)
        print("Stopped")

        # Destroy the line follower object
        del lf


def lf_camera_main(scale:float=30.0, polarity:int=-1, speed:int=22, is_camera:bool=True, cam_thresh:int=50, cam_tilt_angle:int=-25):
    """Main function to follow the line using camera"""

    lf = LineFollower(scale=scale, polarity=polarity, speed=speed, is_camera=is_camera, cam_thresh=cam_thresh)

    # Tilt camera down and point it in front
    lf.set_cam_tilt_angle(cam_tilt_angle)
    lf.set_cam_pan_angle(10) # Based on servo mounting

    try:
        for frame in lf.camera.get_stream():
            # Get the image from the stream
            image = frame.array
            # Follow the line
            lf.follow_line(image=image)

            # Clear the stream
            lf.camera.camStream.truncate(0)

    except KeyboardInterrupt:
        lf.stop()
        lf.zeros_servos()
        print("Stopped")

        # Destroy the line follower object
        del lf.camera
        del lf


def lf_grayscale_concurrent(l_th:float=0.35, h_th:float=0.8, polarity:int=-1, scale:float=30.0, speed:int=22,
                            sdelay:float=0.1, idelay:float=0.1, cdelay:float=0.1, rdelay:float=0.1):
    """Function to run line following using grayscale sensors concurrently"""

    # Create the bus for all three processes
    sensor_bus = Bus()
    interpret_bus = Bus()
    control_bus = Bus()

    # Create the sensor, interpreter and controller objects
    sensor = Sensing()
    interp = Interpret(l_th=l_th, h_th=h_th, polarity=polarity)
    controller = LineFollowControl(scale=scale)

    # Create the executor
    robot = LineFollower(speed=speed)

    try:

        # Start all the processes concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Sensor process
            eSensor = executor.submit(sensor.producer, sensor_bus, sdelay)
            # Interpreter process
            eInterp = executor.submit(interp.consumer_producer, sensor_bus, interpret_bus, idelay)
            # Controller process
            eControl = executor.submit(controller.consumer_producer, interpret_bus, control_bus, cdelay)
            # Robot process
            eRobot = executor.submit(robot.consumer, control_bus, rdelay)

        # Stop the robot
        robot.stop()

        # Error handling
        eSensor.result()
        eInterp.result()
        eControl.result()
        eRobot.result()

    except KeyboardInterrupt:
        print("Concurrent Line Following stopped by User")

        # Stop the robot
        robot.stop()

        # Error handling
        eSensor.result()
        eInterp.result()
        eControl.result()
        eRobot.result()


if __name__ == "__main__":

    # Common Parameters
    scale = 30.0
    polarity = -1
    speed = 22

    # Parameters for grayscale sensors
    l_th = 0.35
    h_th = 0.8
    is_normal = False

    # Parameters for camera
    cam_thresh = 50
    cam_tilt_angle = -25
    is_camera = True

    # Delay for concurrent execution
    sdelay = 0.1
    idelay = 0.1
    cdelay = 0.1
    rdelay = 0.1
    is_concurrent = False

    # Call the main function
    if not is_camera and not is_concurrent:
        # Gray Scale Sensors single process
        lf_grayscale_main(scale=scale, polarity=polarity, speed=speed, l_th=l_th, h_th=h_th, is_normal=is_normal)

    elif is_concurrent and not is_camera:
        # Gray Scale Sensors concurrent processes
        lf_grayscale_concurrent(l_th=l_th, h_th=h_th, polarity=polarity, scale=scale, speed=speed, sdelay=sdelay, idelay=idelay, cdelay=cdelay, rdelay=rdelay)

    elif is_camera and not is_concurrent:
        # Camera single process
        lf_camera_main(scale=scale, polarity=polarity, speed=speed, is_camera=is_camera, cam_thresh=cam_thresh, cam_tilt_angle=cam_tilt_angle)

    elif is_camera and is_concurrent:
        # Camera concurrent processes
        print("Camera concurrent processes not implemented yet!")