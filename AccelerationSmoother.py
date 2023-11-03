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
    def __init__(self, acceleration, max_value = None, min_value = None, initial_value = 0.0, initial_target = 0.0):
        #   constants ish
        self._max_value = max_value
        self._min_value = min_value
        self._acceleration = acceleration

        #   variables
        self._current_acceleration = 0.01 # per second
        self._current_direction = 0 # -1 or 1
        self._current_value = initial_value
        self._current_target = initial_target
        self._last_time = get_current_time()

    def clamp(self, value):
        if self._max_value is not None:
            value = min(value, self._max_value)
        if self._min_value is not None:
            value = max(value, self._min_value)
        return value

    def get_direction(self):
        return self._current_direction

    def update(self, current_target : float = None, print_debug = False, time_difference = None):
        #   update current target
        if current_target is not None:
            self._current_target = current_target

        #   calculate time difference
        if time_difference is None:
            current_time = get_current_time()
            time_difference = current_time - self._last_time
        else:
            self._last_time += time_difference

        if print_debug: print(f"============\n{current_time=}\n{self._last_time=}\n{time_difference=}\n")

        self._current_direction = sign(self._current_target - self._current_value)

        #   calculate speed (DO NOT QUESTION THE BLACK MAGIC)
        # self._current_value += max(min(self._acceleration, abs(self._current_acceleration)), self._acceleration/20) * self._current_direction * time_difference

        # print
        if print_debug: print(f"{self._current_value=}\n{self._current_target=}\n{self._current_direction=}\n")

        # Simple update
        self._current_value += self._acceleration * self._current_direction * time_difference
        if sign(current_target - self._current_value) != self._current_direction:
            if print_debug: print('I am here')
            self._current_value = current_target

        #clamp the value
        self._current_value = self.clamp(self._current_value)

        #   update last time
        self._last_time = get_current_time()

        #   return speed
        return self._current_value
