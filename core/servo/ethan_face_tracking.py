'''
This program was written by Ethan Bui. It receives information about the position of a 
human face within a camera frame, and instruct the servos to move to put the 
face at the centre of the frame.
'''
from faceram import *
import numpy as np
import cv2
from ethan_servo_gesture import (
    move_to, go_home, search, stop_gesture,
    get_position, is_gesture_running
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FRAME_WIDTH  = 2592
FRAME_HEIGHT = 1944

DEADZONE = 81

F_OVER_Z = 0.0036

PREDICTION_SCALE = 0.5

CENTRE_X = FRAME_WIDTH  // 2
CENTRE_Y = FRAME_HEIGHT // 2

# ---------------------------------------------------------------------------
# Tracking state
# ---------------------------------------------------------------------------

_prev_face_x = None
_prev_face_y = None

# ---------------------------------------------------------------------------
# Control loop
# ---------------------------------------------------------------------------

def update_servo(point: np.array) -> None:
    """
    Adjust servo position so the detected face is centred in the frame.
    Uses an interaction matrix (image Jacobian) to map pixel error directly
    to servo angle correction, combined with velocity-based prediction.
    Call this every frame from the detection program.

    Parameters
    ----------
    bbox : tuple  Bounding box of the detected face [x, y].
                  Pass None if no face is detected.
    """
    global _prev_face_x, _prev_face_y

    if point is None:
        _prev_face_x = None
        _prev_face_y = None
        return

    face_centre_x, face_centre_y = point

# Velocity-based prediction

    if _prev_face_x is not None and _prev_face_y is not None:
        velocity_x = face_centre_x - _prev_face_x
        velocity_y = face_centre_y - _prev_face_y
        predicted_x = face_centre_x + velocity_x * PREDICTION_SCALE
        predicted_y = face_centre_y + velocity_y * PREDICTION_SCALE
    else:
        predicted_x = face_centre_x
        predicted_y = face_centre_y

    _prev_face_x = face_centre_x
    _prev_face_y = face_centre_y

    error_x = predicted_x - CENTRE_X
    error_y = predicted_y - CENTRE_Y

    if abs(error_x) > DEADZONE or abs(error_y) > DEADZONE:
        pan_angle, tilt_angle = get_position()
        new_pan  = pan_angle  + F_OVER_Z * error_x
        new_tilt = tilt_angle + F_OVER_Z * error_y
        move_to(new_pan, new_tilt)