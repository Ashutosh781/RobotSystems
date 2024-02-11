import atexit
import logging
import rossros as rr

from sense_interp import Sensing, SenseUltra, Interpret, InterpretUltra
from controller import LineFollowControl
from line_follow import LineFollower
from picarx_improved import Picarx

logging_format = "%(asctime)s: %(message)s"
logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%H:%M:%S")
logging.getLogger().setLevel(logging.DEBUG)


def main(l_th:float=0.35, h_th:float=0.8, polarity:int=-1, obj_th:float=15.0, scale:float=30.0, speed:int=22,
        Gsdelay:float=0.1, Usdelay:float=0.1, Gidelay:float=0.1, Uidelay:float=0.1, cdelay:float=0.1, rdelay:float=0.1,
        terminate_time:int=60):

    # Create objects
    Gsensor = Sensing() # Grayscale sensor
    Usensor = SenseUltra() # Ultrasonic sensor
    Ginterp = Interpret(l_th=l_th, h_th=h_th, polarity=polarity) # Grayscale interpreter
    Uinterp = InterpretUltra(threshold=obj_th) # Ultrasonic interpreter
    controller = LineFollowControl(scale=scale) # Line follow controller
    robot = LineFollower(speed=speed) # Robot

    # Create buses
    bGsensor = rr.Bus(Gsensor.get_grayscale_data(), "Grayscale sensor bus")
    bUsensor = rr.Bus(Usensor.get_ultrasonic_data(), "Ultrasonic sensor bus")
    bGinterp = rr.Bus(Ginterp.get_direction(), "Grayscale interpreter bus")
    bUinterp = rr.Bus(Uinterp.get_obstacle(), "Ultrasonic interpreter bus")
    bControl = rr.Bus(controller.get_control_angle(), "Control Angle bus")
    bTerminate = rr.Bus(0, "Termination Bus")

    # Create producers, consumers and consumers-producers
    readGsensor = rr.Producer(
        Gsensor.get_grayscale_data,  # function that will generate data
        bGsensor,  # output data bus
        Gsdelay,  # delay between data generation cycles
        bTerminate,  # bus to watch for termination signal
        "Read Grayscale sensor signal"
    )

    readUsensor = rr.Producer(
        Usensor.get_ultrasonic_data,  # function that will generate data
        bUsensor,  # output data bus
        Usdelay,  # delay between data generation cycles
        bTerminate,  # bus to watch for termination signal
        "Read Ultrasonic sensor signal"
    )

    interpretGsensor = rr.ConsumerProducer(
        Ginterp.get_direction,  # function that will interpret data
        bGsensor,  # input data bus
        bGinterp,  # output data bus
        Gidelay,  # delay between data interpretation cycles
        bTerminate,  # bus to watch for termination signal
        "Interpret Grayscale sensor signal"
    )

    interpretUsensor = rr.ConsumerProducer(
        Uinterp.get_obstacle,  # function that will interpret data
        bUsensor,  # input data bus
        bUinterp,  # output data bus
        Uidelay,  # delay between data interpretation cycles
        bTerminate,  # bus to watch for termination signal
        "Interpret Ultrasonic sensor signal"
    )

    controlAngle = rr.ConsumerProducer(
        controller.get_control_angle,  # function that will process data
        bGinterp,  # input data bus
        bControl,  # output data bus
        cdelay,  # delay between data control cycles
        bTerminate,  # bus to watch for termination signal
        "Control Angle"
    )

    robotControl = rr.Consumer(
        robot.follow_line_with_ultra,  # function that will run the robot
        (bControl, bUinterp),  # input data buses
        rdelay,  # delay between data control cycles
        bTerminate,  # bus to watch for termination signal
        "Robot Control"
    )

    # Create a termination signal
    termination = rr.Timer(
        bTerminate, # output data bus
        terminate_time, # time to wait before sending termination signal
        0.01, # delay between checking for termination time
        bTerminate, # bus to check for termination signal
        "Termination Timer"
    )

    # List of producer-consumers to execute concurrently
    producer_consumer_list = [readGsensor,
                            readUsensor,
                            interpretGsensor,
                            interpretUsensor,
                            controlAngle,
                            robotControl,
                            termination]

    # Run the concurrent execution
    rr.runConcurrently(producer_consumer_list)

    # Kill the robot
    atexit.register(robot.stop)


if __name__ == "__main__":

    # Parameters
    l_th = 0.35
    h_th = 0.8
    polarity = -1
    obj_th = 15.0
    scale = 30.0
    speed = 22

    # Delays
    Gsdelay = 0.05
    Usdelay = 0.06
    Gidelay = 0.05
    Uidelay = 0.06
    cdelay = 0.06
    rdelay = 0.15

    # Termination time
    terminate_time = 15 # seconds

    # Call the main function
    main(l_th=l_th, h_th=h_th, polarity=polarity, obj_th=obj_th, scale=scale, speed=speed,
        Gsdelay=Gsdelay, Usdelay=Usdelay, Gidelay=Gidelay, Uidelay=Uidelay, cdelay=cdelay, rdelay=rdelay,
        terminate_time=terminate_time)