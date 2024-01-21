import time
import readchar
from maneuvers import Maneuvers

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
    ctrl+c: Exit the program

    Robot will stop before a change of maneuver, it will then execute the maneuver until either the maneuver is complete or the robot is stopped.
'''

def show_info():
    print("\033[H\033[J",end='')  # clear terminal windows
    print(manual)


if __name__ == "__main__":
    try:
        robot = Maneuvers()
        show_info()
        robot.stop()
        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in('qweasdzxc'):
                if 'w' == key:
                    robot.stop()
                    robot.drive_steer(30, 0)
                    print("Forward")
                elif 's' == key:
                    robot.stop()
                    robot.drive_steer(-30, 0)
                    print("Backward")
                elif 'a' == key:
                    robot.stop()
                    robot.drive_steer(30, -20)
                    print("Turn Left")
                elif 'd' == key:
                    robot.stop()
                    robot.drive_steer(30, 20)
                    print("Turn Right")
                elif 'x' == key:
                    robot.stop()
                    print("Stop")
                elif 'q' == key:
                    robot.stop()
                    robot.parallel_park('l')
                    print("Parallel Park Left")
                elif 'e' == key:
                    robot.stop()
                    robot.parallel_park('r')
                    print("Parallel Park Right")
                elif 'z' == key:
                    robot.stop()
                    robot.three_point_turn('l')
                    print("Three Point Turn Left")
                elif 'c' == key:
                    robot.stop()
                    robot.three_point_turn('r')
                    print("Three Point Turn Right")

                time.sleep(0.5)
                show_info()

            elif key == readchar.key.CTRL_C:
                break

    except KeyboardInterrupt:
        robot.stop()
        time.sleep(0.5)
        print("Program Ended")