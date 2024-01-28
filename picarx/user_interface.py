import time
import readchar
from maneuvers import Maneuvers
from line_follow import main as line_follow_main

manual = '''
Press keys on keyboard to control PiCar-X!
    w: Forward
    a: Turn left
    s: Backward
    d: Turn right
    x: Stop
    q: Parallel park to the left
    e: Parallel park to the right
    z: Three point turn to the left
    c: Three point turn to the right
    f: Line following - Be careful to kill the program
    ctrl+c: Exit the program

    Robot will execute a maneuver until either the maneuver is complete or the robot is stopped.
    For safety reasons, keep the Stop key (x) close at hand.
    For best and safe results, explicit speed and angle values are used for each maneuver, and not controlled by the user.
    For complex maneuvers, parallel parking and three point turn, the robot will execute the maneuver completely, before accepting another command.
'''

def show_info():
    # Clear the screen
    print("\033[H\033[J",end='')
    # Print the manual
    print(manual)


if __name__ == "__main__":
    try:
        # Create a maneuver object
        robot = Maneuvers()
        show_info()

        # Stop the robot initially for safety
        robot.stop()

        # Set the speed and angle
        speed = robot.SAFE_SPEED
        angle = robot.SAFE_ANGLE
        line_follow_speed = 20

        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in('qweasdzxcf'):
                if 'w' == key:
                    robot.drive_steer(speed, 0)
                    print("Forward")
                elif 's' == key:
                    robot.drive_steer(-speed, 0)
                    print("Backward")
                elif 'a' == key:
                    robot.drive_steer(speed, -angle)
                    print("Turn Left")
                elif 'd' == key:
                    robot.drive_steer(speed, angle)
                    print("Turn Right")
                elif 'x' == key:
                    robot.stop()
                    print("Stop")
                elif 'q' == key:
                    robot.parallel_park('l')
                    print("Parallel Park Left")
                elif 'e' == key:
                    robot.parallel_park('r')
                    print("Parallel Park Right")
                elif 'z' == key:
                    robot.three_point_turn('l')
                    print("Three Point Turn Left")
                elif 'c' == key:
                    robot.three_point_turn('r')
                    print("Three Point Turn Right")

                elif 'f' == key:
                    # Parameters for line following
                    scale = 30.0
                    l_th = 0.35
                    h_th = 0.8
                    polarity = -1
                    is_normal = False
                    # Create a line follower object
                    print("Line Following")
                    lf = line_follow_main(scale, l_th, h_th, polarity, line_follow_speed, is_normal)

                time.sleep(0.1)
                show_info()

            elif key == readchar.key.CTRL_C:
                break

    except KeyboardInterrupt:
        robot.stop()
        time.sleep(0.25)
        print("Program Ended")