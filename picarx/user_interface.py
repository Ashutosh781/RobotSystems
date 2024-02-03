import time
import readchar
from maneuvers import Maneuvers
from line_follow import lf_grayscale_main, lf_camera_main, lf_grayscale_concurrent

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
    f: Line following - grayscale
    r: Line following - camera
    v: Line following - grayscale concurrent
    ctrl+c: Exit the program

    Robot will execute a maneuver until either the maneuver is complete or the robot is stopped.
    For safety reasons, keep the Stop key (x) close at hand.
    For best and safe results, explicit speed and angle values are used for each maneuver, and not controlled by the user.
    For complex maneuvers, parallel parking and three point turn, the robot will execute the maneuver completely, before accepting another command.

    For line following using grayscale sensors, sometimes killing the process doesn't terminate the program. In such cases, use ctrl+z to stop the program, and then run it again.
    For line following using camera, you can only do it once in a session. If you want to do it again, you need to restart the program.
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

        # Parameters for manual control
        speed = robot.SAFE_SPEED
        angle = robot.SAFE_ANGLE
        line_follow_speed = 22
        line_follow_scale = 30.0
        line_follow_polarity = -1

        while True:
            key = readchar.readkey()
            key = key.lower()
            if key in('qweasdzxcfrv'):
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
                    # Parameters for line following using grayscale sensors
                    l_th = 0.35
                    h_th = 0.8
                    is_normal = False

                    # Create a line follower object
                    print("Line Following using Grayscale Sensors")
                    lf_grayscale_main(scale=line_follow_scale, polarity=line_follow_polarity, speed=line_follow_speed,
                                        l_th=l_th, h_th=h_th, is_normal=is_normal)

                elif 'r' == key:
                    # Parameters for line following using camera
                    cam_thresh = 50
                    cam_tilt_angle = -25
                    is_camera = True

                    # Create a line follower object
                    print("Line Following using Camera")
                    lf_camera_main(scale=line_follow_scale, polarity=line_follow_polarity, speed=line_follow_speed,
                                    is_camera=is_camera, cam_thresh=cam_thresh, cam_tilt_angle=cam_tilt_angle)

                elif 'v' == key:
                    # Parameters for line following using grayscale sensors
                    l_th = 0.35
                    h_th = 0.8
                    sdelay = 0.1
                    idelay = 0.1
                    cdelay = 0.1
                    rdelay = 0.1

                    # Create a line follower object
                    print("Line Following using Grayscale Sensors - Concurrent")
                    lf_grayscale_concurrent(l_th=l_th, h_th=h_th, polarity=line_follow_polarity, scale=line_follow_scale,
                                            speed=line_follow_speed, sdelay=sdelay, idelay=idelay, cdelay=cdelay, rdelay=rdelay)

                time.sleep(0.1)
                show_info()

            elif key == readchar.key.CTRL_C:
                break

    except KeyboardInterrupt:
        robot.stop()
        time.sleep(0.1)
        print("Program Ended")