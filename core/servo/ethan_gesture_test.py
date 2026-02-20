'''
This Python program was written by Ethan Bui. The program tests how well do the 
servos move according to the given gestures.
'''

from ethan_servo_gesture import (
    move_to, go_home, scan, nod, search,
    stop_gesture, get_position
)
from time import sleep

print("=== Gesture Test Mode ===")
print("Available gestures:")
print("  home   →  Return to home position")
print("  nod    →  Nod gesture")
print("  scan   →  Scan gesture")
print("  search →  Full search pattern")
print("  move   →  Move to a specific angle")
print("  q      →  Quit")

go_home()

while True:

    gesture_input = input("\nEnter gesture: ").strip().lower()

    if gesture_input == 'q':
        print("Exiting gesture test.")
        break

    elif gesture_input == 'home':
        print("Moving to home position...")
        go_home()

    elif gesture_input == 'nod':
        print("Executing nod gesture...")
        nod(blocking=True)

    elif gesture_input == 'scan':
        print("Executing scan gesture...")
        scan(blocking=True)

    elif gesture_input == 'search':
        print("Executing full search pattern...")
        search(blocking=True)

    elif gesture_input == 'move':
        try:
            pan_input  = input("  Enter PAN angle (0-180): ")
            tilt_input = input("  Enter TILT angle (0-180): ")
            pan_angle  = float(pan_input)
            tilt_angle = float(tilt_input)
            print(f"Moving to PAN: {pan_angle}  TILT: {tilt_angle}")
            move_to(pan_angle, tilt_angle, duration=0.5)
        except ValueError:
            print("Invalid input. Enter a number.")

    else:
        print("Unknown gesture. Try: home, nod, scan, search, move, q")