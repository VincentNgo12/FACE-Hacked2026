'''
This program was written by Ethan Bui. It receives information about the position of a 
human face within a camera frame, and instruct the servos to move to put the 
face at the centre of the frame.
'''

from ethan_servo_gesture import (
    move_to, go_home, search, stop_gesture,
    get_position, is_gesture_running
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRAME_WIDTH  = 2592
FRAME_HEIGHT = 1944

# How close the face centre needs to be to the frame centre before
# the system considers it "centred" and stops correcting (in pixels)
DEADZONE = 80

# Scaling factor — controls how aggressively the servo corrects.
# Higher = faster correction but may overshoot.
PAN_SCALE  = 0.03   # degrees of servo movement per pixel of error
TILT_SCALE = 0.03

# Frame centre
CENTRE_X = FRAME_WIDTH  // 2
CENTRE_Y = FRAME_HEIGHT // 2

# ---------------------------------------------------------------------------
# Control loop
# ---------------------------------------------------------------------------

def update_servo(bbox: tuple) -> None:
    """
    Adjust servo position so the detected face is centred in the frame.
    Call this every frame from the detection program.

    Parameters
    ----------
    bbox : tuple  Bounding box of the detected face (x, y, width, height).
                  Pass None if no face is detected.
    """
    if bbox is None:
        # No face detected — trigger search if not already searching
        if not is_gesture_running():
            search()
        return

    # Stop any running gesture the moment a face is detected
    if is_gesture_running():
        stop_gesture()

    x, y, width, height = bbox

    # Calculate face centre
    face_centre_x = x + width  // 2
    face_centre_y = y + height // 2

    # Calculate error from frame centre
    error_x = face_centre_x - CENTRE_X   # Positive = face is to the right
    error_y = face_centre_y - CENTRE_Y   # Positive = face is below centre

    # Only correct if outside the deadzone
    if abs(error_x) > DEADZONE or abs(error_y) > DEADZONE:
        pan_angle, tilt_angle = get_position()

        new_pan  = pan_angle  + error_x * PAN_SCALE
        new_tilt = tilt_angle + error_y * TILT_SCALE

        move_to(new_pan, new_tilt)