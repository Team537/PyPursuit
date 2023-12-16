import time

def clamp(value: float | int, min_value: float | int, max_value: float | int):
    """
    This function clamps a value between a max and min value
    :param value:
    :param max_value:
    :param min_value:
    :return:
    """
    if max_value is not None:
        value = min(value, max_value)
    if min_value is not None:
        value = max(value, min_value)
    return value

def get_current_time():
    return round(time.time_ns() / 1e9, 3)

def sign(x):
    """
    Returns the sign of the number: 1 if positive, -1 if negative, 0 if 0
    :param x:
    :return:
    """
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0
