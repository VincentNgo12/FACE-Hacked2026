'''
This program was written by Ethan Bui. It instructs a pair of servo to do
nod and scan gestures to search for a human face.
'''

from gpiozero import AngularServo
from time import sleep
import threading
import math


# Setting parameters for the two servos

PAN_PIN  = 18
TILT_PIN = 19

PAN_MIN,  PAN_MAX  = 0, 180
TILT_MIN, TILT_MAX = 0, 180

HOME_PAN  = 45   # Centre position
HOME_TILT = 45

MIN_PULSE = 0.0005
MAX_PULSE = 0.0025


# Initialisation

pan = AngularServo(PAN_PIN,
                   min_angle=PAN_MIN, max_angle=PAN_MAX,
                   min_pulse_width=MIN_PULSE, max_pulse_width=MAX_PULSE)

tilt = AngularServo(TILT_PIN,
                    min_angle=TILT_MIN, max_angle=TILT_MAX,
                    min_pulse_width=MIN_PULSE, max_pulse_width=MAX_PULSE)

# Internal state

_current_pan  = HOME_PAN
_current_tilt = HOME_TILT

# Stop any running gestures
_stop_event = threading.Event()

# Prevents multiple gestures running at the same time
_gesture_lock = threading.Lock()


# Low-level helper functions

def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _set_pan(angle: float) -> None:
    global _current_pan
    angle = _clamp(angle, PAN_MIN, PAN_MAX)
    pan.angle = angle
    _current_pan = angle


def _set_tilt(angle: float) -> None:
    global _current_tilt
    angle = _clamp(angle, TILT_MIN, TILT_MAX)
    tilt.angle = angle
    _current_tilt = angle


# Smooth trajectory — eased movement between two angles

def _ease_in_out(t: float) -> float:
    """
    Smoothstep easing function.
    t is in [0, 1]. Returns a value in [0, 1] with smooth acceleration
    and deceleration at the start and end of the move.
    """
    return t


def move_to(target_pan: float, target_tilt: float,
            duration: float = 0.5, steps: int = 50) -> bool:
    """
    Smoothly move both servos from their current positions to the target
    angles over `duration` seconds using eased interpolation.

    Returns True if the move completed, False if it was interrupted.

    Parameters
    ----------
    target_pan   : float  Target pan angle  (0–180)
    target_tilt  : float  Target tilt angle (0–135)
    duration     : float  Time in seconds for the full move (default 0.5s)
    steps        : int    Number of intermediate positions (default 50)
    """
    start_pan  = _current_pan
    start_tilt = _current_tilt
    target_pan  = _clamp(target_pan,  PAN_MIN,  PAN_MAX)
    target_tilt = _clamp(target_tilt, TILT_MIN, TILT_MAX)
    interval = duration / steps

    for i in range(1, steps + 1):
        if _stop_event.is_set():
            return False

        t = _ease_in_out(i / steps)
        _set_pan(start_pan   + t * (target_pan  - start_pan))
        _set_tilt(start_tilt + t * (target_tilt - start_tilt))
        sleep(interval)

    return True


def go_home(duration: float = 0.5) -> bool:
    """Move both servos to the home (centre) position."""
    return move_to(HOME_PAN, HOME_TILT, duration=duration)


# ---------------------------------------------------------------------------
# Gesture library
# ---------------------------------------------------------------------------

def _run_gesture(fn, *args, **kwargs):
    """
    Run a gesture function in a background thread.
    Acquires the gesture lock so only one gesture runs at a time.
    Clears the stop event before starting.
    """
    def _wrapper():
        with _gesture_lock:
            _stop_event.clear()
            fn(*args, **kwargs)

    t = threading.Thread(target=_wrapper, daemon=True)
    t.start()
    return t


def stop_gesture() -> None:
    """
    Interrupt any currently running gesture immediately.
    The servos will hold their position at the point of interruption.
    Call this as soon as the vision system detects the target.
    """
    _stop_event.set()


# -- Scan -------------------------------------------------------------------

def scan(pan_start: float = PAN_MIN, pan_end: float = PAN_MAX,
         tilt_angle: float = None,
         sweep_duration: float = 2.0,
         sweeps: int = 1,
         blocking: bool = False):
    """
    Sweep the pan axis from pan_start to pan_end and back, at a fixed
    tilt angle. Used when searching for a lost target.

    Parameters
    ----------
    pan_start      : float  Left boundary of the sweep  (default 0°)
    pan_end        : float  Right boundary of the sweep (default 180°)
    tilt_angle     : float  Tilt to hold during scan. None = current tilt.
    sweep_duration : float  Time for one full left→right sweep (default 2s)
    sweeps         : int    Number of left→right→left cycles (default 1)
    blocking       : bool   If True, block until gesture finishes.
    """
    def _scan():
        hold_tilt = tilt_angle if tilt_angle is not None else _current_tilt

        # Move to the start position first
        if not move_to(pan_start, hold_tilt, duration=0.4):
            return

        for _ in range(sweeps):
            # Sweep right
            if not move_to(pan_end, hold_tilt, duration=sweep_duration):
                return
            # Sweep left
            if not move_to(pan_start, hold_tilt, duration=sweep_duration):
                return

        # Return to home after completing all sweeps
        go_home()

    if blocking:
        _stop_event.clear()
        _scan()
    else:
        return _run_gesture(_scan)


# -- Nod --------------------------------------------------------------------

def nod(tilt_up: float = 60, tilt_down: float = 120,
        repeats: int = 2, speed: float = 0.4,
        blocking: bool = False):
    """
    Nod the tilt axis up and down. Used as a searching behaviour on the
    vertical axis, or as a confirmation signal when the target is centred.

    Parameters
    ----------
    tilt_up   : float  Upper tilt limit for the nod  (default 60°)
    tilt_down : float  Lower tilt limit for the nod  (default 120°)
    repeats   : int    Number of up-down cycles       (default 2)
    speed     : float  Duration of each half-stroke   (default 0.4s)
    blocking  : bool   If True, block until gesture finishes.
    """
    def _nod():
        hold_pan = _current_pan

        for _ in range(repeats):
            if not move_to(hold_pan, tilt_up,   duration=speed): return
            if not move_to(hold_pan, tilt_down, duration=speed): return

        # Return to home after nodding
        go_home()

    if blocking:
        _stop_event.clear()
        _nod()
    else:
        return _run_gesture(_nod)


# -- Search (combined pan + tilt sweep) -------------------------------------

def search(blocking: bool = False):
    """
    Combined search pattern: scan left-right at three different tilt angles
    to cover the full field of view. If no face is detected after a full
    search, repeats up to 2 more times (3 total).

    Parameters
    ----------
    blocking               : bool      If True, block until gesture finishes.
    """
    def _search():
        max_attempts = 3

        for attempt in range(max_attempts):
            if _stop_event.is_set():
                return

            tilt_positions = [45, 90, 135]

            for i, tilt_pos in enumerate(tilt_positions):
                print("bfr sleep")
                sleep(5)
                print("aft sleep")
                if _stop_event.is_set():
                    return

                # Step 1: Move tilt to position while keeping pan where it is
                if not move_to(_current_pan, tilt_pos, duration=0.5):
                    return

                # Step 2: Move pan back to PAN_MIN
                if not move_to(PAN_MIN, tilt_pos, duration=1.5):
                    return

                # Step 3: Sweep pan from PAN_MIN to PAN_MAX at fixed tilt
                if not move_to(PAN_MAX, tilt_pos, duration=2.0):
                    return

            print(f"Search attempt {attempt + 1} of {max_attempts} complete, no face detected.")

        print("No face detected after all attempts.")
        go_home()

    if blocking:
        _stop_event.clear()
        _search()
    else:
        return _run_gesture(_search)

# ---------------------------------------------------------------------------
# Status helpers
# ---------------------------------------------------------------------------

def get_position() -> tuple:
    """Return the current (pan, tilt) angles."""
    return (_current_pan, _current_tilt)


def is_gesture_running() -> bool:
    """Return True if a gesture is currently executing."""
    return _gesture_lock.locked()


# ---------------------------------------------------------------------------
# Quick demo — runs when this file is executed directly
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Moving to home position...")
    go_home(duration=0.8)
    sleep(1)

    print("Demonstrating smooth move_to...")
    move_to(45, 60, duration=1.0)
    sleep(0.5)
    move_to(135, 120, duration=1.0)
    sleep(0.5)
    go_home()
    sleep(1)

    print("Demonstrating nod (blocking)...")
    nod(blocking=True)
    sleep(1)

    print("Demonstrating scan (blocking)...")
    scan(blocking=True)
    sleep(1)

    print("Demonstrating full search pattern (blocking)...")
    search(blocking=True)
    sleep(1)

    print("Done. Servos at home position.")