from Utils.UtilFuncs import sign, clamp, get_current_time

class AccelerationSmoother:
    def __init__(self, acceleration, max_value: float | None = None, min_value: float | None = None,
                 initial_value=0.0,
                 initial_target=0.0):
        #   constants ish
        self._max_value = max_value
        self._min_value = min_value
        self._acceleration = acceleration

        #   variables
        self._current_acceleration = 0.01  # per second
        self._current_direction = 0  # -1 or 1
        self._current_value = initial_value
        self._current_target = initial_target
        self._last_time = get_current_time()

    def set_state(self, value):
        self._current_value = value
        self._current_target = value
        self._current_direction = 0
        self._current_acceleration = 0

    def get_direction(self):
        return self._current_direction

    def get_value(self):
        return self._current_value

    def update(self, current_target: float = None, time_difference=None) -> float:
        #   update current target
        if current_target is not None:
            self._current_target = current_target

        #   calculate time difference
        if time_difference is None:
            current_time = get_current_time()
            time_difference = current_time - self._last_time
        else:
            self._last_time += time_difference

        #   Actual code
        self._current_direction = sign(self._current_target - self._current_value)

        # Simple update
        self._current_value += self._acceleration * self._current_direction * time_difference
        if sign(current_target - self._current_value) != self._current_direction:
            self._current_value = current_target

        # clamp the value
        self._current_value = clamp(self._current_value, self._min_value, self._max_value)

        #   update last time
        self._last_time = get_current_time()

        #   return speed
        return self._current_value
