import time
import cv2 as cv
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray


class CameraHandle(object):
    """Class to handle capture of images from the picamera and detect line angles for lane following

    Args:
        polarity: Polarity of the line (-1 for black line on white background, 1 for white line on black background)
        thresh: Threshold for line detection
    """

    def __init__(self, polarity:int=-1, thresh:int=50):
        """Initialise the camera"""

        # Arguments
        self.polarity = polarity
        self.thresh = thresh

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

        # Initialise the region of interest
        self.roi = ROI()

        # Hyperparameters for line detection
        self.gaussian_kernel = (9, 9)

    def get_stream(self):
        """Get camera stream"""

        # Generate a continuous stream of images from the camera
        gen = self.camera.capture_continuous(self.camStream, format='bgr', use_video_port=True)

        return gen

    def get_shift(self, image, is_draw:bool=False):

        # Extract dimensions of the image
        height, width = image.shape[:2]
        w = int(width / 2)

        # Initialise the region of interest
        if self.roi.get_area() == 0:
            self.roi.init_roi(width, height)

        # Preprocess the image
        gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) # convert to grayscale
        blur = cv.GaussianBlur(gray, self.gaussian_kernel, 0) # apply Gaussian blur

        # Working variables
        polarity = 0
        threshold = None
        box = None
        countour = None
        pt1 = None
        pt2 = None
        shift = None

        # Threshold the image
        if self.polarity == -1:
            polarity = cv.THRESH_BINARY_INV

        _, threshold = cv.threshold(blur, self.thresh, 255, polarity)

        # Crop the image
        crop = self.roi.crop_roi(threshold)

        # Find main contour in the cropped image
        if crop is not None:
            cnts, _ = cv.findContours(crop, cv.RETR_CCOMP, cv.CHAIN_APPROX_SIMPLE)
            countour = None
            if cnts is not None and len(cnts) > 0:
                countour = max(cnts, key=cv.contourArea)

            # Find the box around the contour
            if countour is not None:
                rect = cv.minAreaRect(countour)
                box = cv.boxPoints(rect)
                box = np.int0(box)
                box = self.roi.order_box(box)

                # Calculate the average shift of the line
                # We are tracking the average shift of the line because just tracking the center of the line might result in early turns
                if box is not None:
                    pt1, pt2 = self.roi.calc_box_vector(box)

                    if pt1 is not None and pt2 is not None:
                        s1 = (pt1[0] - w) / w
                        s2 = (pt2[0] - w) / w
                        shift = (s1 + s2) / 2

                        # Draw the countour, box and line on the image
                        if is_draw:
                            cv.drawContours(image, [countour], -1, (0, 0, 255), 3)
                            cv.drawContours(image, [box], 0, (255, 0, 0), 2)
                            cv.line(image, pt1, pt2, (0, 255, 0), 3)
                            msg_shift = f"Shift: {shift}"
                            cv.putText(image, msg_shift, (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return shift


class ROI:
    area = 0
    vertices = None

    def init_roi(self, width, height):
        # Original
        vertices = [(0, height), (width / 4, 3 * height / 4),(3 * width / 4, 3 * height / 4), (width, height)]
        # Edited
        # vertices = [(0, height), (width / 5, 1 * height / 2),(4 * width / 5, 1 * height / 2), (width, height)]
        self.vertices = np.array([vertices], np.int32)

        blank = np.zeros((height, width, 3), np.uint8)
        blank[:] = (255, 255, 255)
        blank_gray = cv.cvtColor(blank, cv.COLOR_BGR2GRAY)
        blank_cropped = self.crop_roi(blank_gray)
        self.area = cv.countNonZero(blank_cropped)

    def crop_roi(self, img):
        mask = np.zeros_like(img)
        match_mask_color = 255

        cv.fillPoly(mask, self.vertices, match_mask_color)
        masked_image = cv.bitwise_and(img, mask)
        return masked_image

    def get_area(self):
        return self.area

    def get_vertices(self):
        return self.vertices

    def order_box(self, box):
        srt = np.argsort(box[:, 1])
        btm1 = box[srt[0]]
        btm2 = box[srt[1]]

        top1 = box[srt[2]]
        top2 = box[srt[3]]

        bc = btm1[0] < btm2[0]
        btm_l = btm1 if bc else btm2
        btm_r = btm2 if bc else btm1

        tc = top1[0] < top2[0]
        top_l = top1 if tc else top2
        top_r = top2 if tc else top1

        return np.array([top_l, top_r, btm_r, btm_l])

    def calc_line_length(self, p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return np.sqrt(dx * dx + dy * dy)

    def calc_box_vector(self, box):
        v_side = self.calc_line_length(box[0], box[3])
        h_side = self.calc_line_length(box[0], box[1])
        idx = [0, 1, 2, 3]
        if v_side < h_side:
            idx = [0, 3, 1, 2]

        pt1 = ((box[idx[0]][0] + box[idx[1]][0]) / 2, (box[idx[0]][1] + box[idx[1]][1]) / 2)
        pt2 = ((box[idx[2]][0] + box[idx[3]][0]) / 2, (box[idx[2]][1]  +box[idx[3]][1]) / 2)

        # Integer
        pt1 = (int(pt1[0]), int(pt1[1]))
        pt2 = (int(pt2[0]), int(pt2[1]))

        return pt1, pt2


if __name__ == "__main__":

    handle = CameraHandle(polarity=-1, thresh=50)

    # Just for camera testing
    from picarx_improved import Picarx

    robot = Picarx()
    robot.set_cam_tilt_angle(-25)
    robot.set_cam_pan_angle(10)

    try:
        for frame in handle.get_stream():
            # Get the image from the stream
            image = frame.array
            # Get the shift of the line
            shift = handle.get_shift(image, is_draw=True)

            # Display the image and edges
            cv.imshow('Image', image)

            key = cv.waitKey(1) & 0xFF

            # Clear the stream
            handle.camStream.truncate(0)

            # Break the loop if 'q' is pressed
            if key == ord('q'):
                robot.zeros_servos()
                cv.destroyAllWindows()
                del robot
                del handle
                break

    except KeyboardInterrupt:
        robot.zeros_servos()
        cv.destroyAllWindows()
        del robot
        del handle
        print("Program Ended")