import time
from controller import LineFollowControl
from sense_interp import Interpret
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

        if direction is None:
            direction = self.prev_direction

        # Get the control angle
        angle = self.controller.get_control_angle(direction)

        self.prev_direction = direction

        # Drive forward with the control angle
        self.forward_with_angle(self.speed, angle)


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

def lf_camera_main(scale:float=30.0, polarity:int=-1, speed:int=22, is_camera:bool=True, cam_thresh:int=50, cam_tilt_angle:int=-15):
    """Main function to follow the line using camera"""

    lf = LineFollower(scale=scale, polarity=polarity, speed=speed, is_camera=is_camera, cam_thresh=cam_thresh)

    # Tilt camera down
    lf.set_cam_tilt_angle(cam_tilt_angle)

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
        lf.set_dir_servo_angle(0.0)
        lf.set_cam_tilt_angle(0.0)
        print("Stopped")

        # Destroy the line follower object
        del lf.camera
        del lf


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
    is_camera = True

    # Call the main function
    if not is_camera:
        lf_grayscale_main(scale=scale, polarity=polarity, speed=speed, l_th=l_th, h_th=h_th, is_normal=is_normal)
    else:
        lf_camera_main(scale=scale, polarity=polarity, speed=speed, is_camera=is_camera, cam_thresh=cam_thresh)