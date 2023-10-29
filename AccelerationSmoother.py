import time


def sign(n):
    if n < 0:
        return -1
    elif n > 0:
        return 1
    else:
        return 0


def get_current_time():
    return round(time.time_ns()/1e9, 3)


class AccelerationSmoother:
    def __init__(self, acceleration, initial_value = 0.0, initial_target = 0.0):
        #   constants ish
        self._acceleration = acceleration

        #   variables
        self._current_acceleration = 0.01 # per second
        self._current_direction = 0 # -1 or 1
        self._current_value = initial_value
        self._current_target = initial_target
        self._last_time = get_current_time()

    def get_direction(self):
        return self._current_direction

    def update(self, current_time = None, current_target : float = None, print_debug = False):
        #   update current target
        if current_target is not None:
            self._current_target = current_target

        if current_time is None:
            current_time = get_current_time()

        #   calculate time difference
        time_difference = current_time - self._last_time
        if print_debug: print(f"============\n{current_time=}\n{self._last_time=}\n{time_difference=}\n")

        self._current_direction = sign(self._current_target - self._current_value)

        #   calculate acceleration
        #getting super close = slow down
        # if abs(self._current_target - self._current_value) < abs(time_difference * self._current_acceleration / self._acceleration):
        #     if print_debug: print("super close")
        #     self._current_acceleration -= abs(self._acceleration) * self._current_direction * time_difference # slow down
        #
        # #super far away = speed up
        # elif abs(self._current_target - self._current_value) > abs(time_difference * self._current_acceleration / self._acceleration):
        #     self._current_acceleration += abs(self._acceleration) * self._current_direction * time_difference # speed up
        #     if print_debug: print("super far")
        # else:
        #     if print_debug: print("max acceleration")
        #
        # if print_debug: print(f"distance to target {abs(self._current_target - self._current_value)}\n{self._current_acceleration=}\n{self._current_target=}\n{self._current_value=}\n{self._current_direction=}\n")

        #   calculate speed
        self._current_value += max(min(self._acceleration, abs(self._current_acceleration)), self._acceleration/20) * self._current_direction * time_difference

        # print
        if print_debug: print(f"{self._current_value=}\n{self._current_target=}\n{self._current_direction=}\n")

        # Simple update
        self._current_value += self._acceleration * self._current_direction * time_difference
        if sign(current_target - self._current_value) != self._current_direction:
            if print_debug: print('I am here')
            self._current_value = current_target
        #   update last time
        self._last_time = get_current_time()

        #   return speed
        return self._current_value
