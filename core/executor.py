import ctypes
import random
import yaml

ctypes.windll.shcore.SetProcessDpiAwareness(1)    # Enable DPI awareness
import pydirectinput

from utils import log
from core.evaluator import evaluate, CONDITION_MAP, compare_picture

"""
description: str
resolution: [int, int]
actions: list / dict
- type: "log"
  message: str
- type: "script"
  name: str
- type: "click" / "move" / "dragTo" / "mouseDown" / "mouseUp" / "keyDown" / "keyUp" / "press" / ...
  args: list
  target:
    CONDITION_MAP
  randomness:
    variance: int
  kwargs: dict
    ...
    tween: pytweening.__attr__
- type: "wait"
  duration: float
  randomness:
    variance: float
    deviation: float
  condition:
    delay: float
    ...
"""

# Utility functions for common actions
# Randomization functions
def random_pos(pos: tuple, variance: int):
    """Return a position around the given value with some variance."""
    x = random.randint(pos[0] - variance, pos[0] + variance)
    y = random.randint(pos[1] - variance, pos[1] + variance)
    return (x, y)

def random_sec(sec: float, variance: float, deviation: float):
    """Return a float around the given value with some variance."""
    import random
    return random.uniform((1-deviation) * sec - variance, (1+deviation) * sec + variance)

# Execution
def wait(action: dict):
    """Wait for a specified duration, with optional randomization."""
    import time

    # Wait until the condition is met
    if condition := action.get("condition"):
        delay = condition.get("delay", 1)
        waiting = True
        while waiting:
            if evaluate(condition):
                break
            time.sleep(delay)
        return True

    # Wait for the specified duration
    duration = action.get("duration", 1)
    randomness = action.get("randomness")
    try:
        variance = randomness.get("variance", 0.0)
        deviation = randomness.get("deviation", 0.0)
    except AttributeError:
        variance = 0.0
        deviation = 0.9
    
    duration = random_sec(float(duration), float(variance), float(deviation))
    time.sleep(duration)

    return True

def click(action: dict):
    """Perform a bot action using pydirectinput, with optional randomization and tweening."""
    args = action.get("args")
    if not isinstance(args, list):
        args = [args] if args is not None else []

    # Handle button targetting if specified
    if target := action.get("target"):
        args = compare_picture(target)

        if not args:
            log.warning(f"No position found for action {action['type']}.")
            return False

    # Handle position randomization if specified
    if randomness := action.get("randomness"):
        variance = int(randomness.get("variance", 20))
        args = random_pos(args, variance)

    # Handle tweening if specified
    kwargs = action.get("kwargs", {})
    if "tween" in kwargs:
        import pytweening
        tween_func = getattr(pytweening, kwargs["tween"])
        kwargs["tween"] = tween_func
    
    func = getattr(pydirectinput, action["type"])
    try:
        func(*args, **kwargs)
    except TypeError:
        log.error(f"No action found for action {action['type']}")
        exit()

    return True

ACTION_MAP = {
    "wait": wait,
    "log": lambda action: log.info(action["message"]) or True,
    "script": lambda action: load_script(action["name"]),
    **{k: click for k in pydirectinput.__dict__.keys()},
}

def load_script(filename: str):
    # Load the script
    try:
        with open(filename, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        log.error(e)
        return False
    
    if desc := config.get("description"):
        log.info(desc)
    
    resolution = tuple(config.get("resolution", []))
    if resolution and pydirectinput.size() != resolution:
        log.error(f"Current resolution {pydirectinput.size()} does not match required {resolution}.")
        return False

    return execute(config.get("actions", []))

def execute(actions: list):
    if not isinstance(actions, list):
        actions = [actions]
    
    for action in actions:
        try:
            action_type = action.get("type")
            func = ACTION_MAP.get(action_type) or CONDITION_MAP.get(action_type)
            result = func(action)
        except TypeError as e:
            log.error(f"Unknown action type: {action_type}")
            log.error(f"Error: {e}")
            return False

        if not result:
            if else_block := action.get("else"):
                log.debug(f"Action/Condition {action_type} failed. Executing 'else' block.")
                execute(else_block)
            else:
                log.warning(f"Action/Condition {action_type} failed and no 'else' block provided. Existing.")
                return False
    
    return True
