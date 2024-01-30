import time
import cv2 as cv
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray


class CameraHandle(object):
    """Class to handle capture of images from the picamera and detect line angles for lane following"""

    def __init__(self):
        """Initialise the camera"""

        # Create a camera object
        self.camera = PiCamera()
        # Set the camera resolution and framerate
        self.camera.resolution = (640, 480)
        self.camera.framerate = 30 # frames per second

        # Create a camera stream object
        self.camStream = PiRGBArray(self.camera, size=(640, 480))
        # Clear the stream
        self.camStream.truncate(0)
        # Wait for the camera to warm up
        time.sleep(1)

    def get_stream(self):
        """Get camera stream"""

        # Generate a continuous stream of images from the camera
        gen = self.camera.capture_continuous(self.camStream, format='bgr', use_video_port=True)

        return gen

    def get_shift(self, image):

        # Preprocess the image
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) # convert to grayscale
        blur = cv.GaussianBlur(gray, (5, 5), 0) # apply Gaussian blur
        edges = cv.Canny(blur, 75, 125) # apply Canny edge detection

    def get_line_angles(self, image, scale, l_th, h_th, polarity, is_normal):
        """Detect the line angles in the image and return the angles"""

        # Convert the image to grayscale
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        # Apply Gaussian blur to the image
        blur = cv.GaussianBlur(gray, (5, 5), 0)
        # Apply Canny edge detection to the image
        edges = cv.Canny(blur, 75, 125)
        # Apply a Hough transform to the image
        lines = cv.HoughLines(edges, 1, np.pi / 180, 70)

        # Check if any lines were detected
        if lines is not None:
            # Create an empty list to store the angles
            angles = []
            # Iterate through each line
            for line in lines:
                # Get the rho and theta values for the line
                rho, theta = line[0]
                # Calculate the angle of the line
                angle = theta * 180 / np.pi
                # Check if the angle is within the specified range
                if l_th < angle < h_th:
                    # Append the angle to the list
                    angles.append(angle)
                    # Draw the line on the image
                    self.draw_line(image, rho, theta)
            # Check if any angles were detected
            if angles:
                # Calculate the mean of the angles
                mean_angle = np.mean(angles)
                # Calculate the steering angle
                steering_angle = int(polarity * (90 - mean_angle))
                # Draw the steering angle on the image
                self.draw_steering_angle(image, steering_angle)
                # Check if the image should be displayed normally or flipped
                if is_normal:
                    # Display the image normally
                    cv.imshow('Line Detection', image)
                else:
                    # Flip the image
                    image = cv.flip(image, 1)
                    # Display the image flipped
                    cv.imshow('Line Detection', image)
                # Return the steering angle
                return steering_angle
            else:
                # Return None if no angles were detected
                return None
        else:
            # Return None if no lines were detected
            return None


if __name__ == "__main__":

    handle = CameraHandle()

    try:
        for frame in handle.get_stream():
            # Get the image from the stream
            image = frame.array
            cv.imshow('Image', image)
            key = cv.waitKey(1) & 0xFF

            # Clear the stream
            handle.camStream.truncate(0)

            # Break the loop if 'q' is pressed
            if key == ord('q'):
                break

    except KeyboardInterrupt:
        cv.destroyAllWindows()
        print("Program Ended")