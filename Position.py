import math
from Rotation import Rotation
from Translation import Translation


class Position(Translation):
    def __init__(self, x, y, rotation : float | Rotation = Rotation(0)):
        super().__init__(x, y)
        self.rotation = Rotation(rotation) # in degrees

    def get_rotation_to(self, other):
        return Rotation.distance_to(self.rotation, other.rotation)

    def get_angle_to(self, other):
        return Rotation((math.atan2(other.y - self.y, other.x - self.x) * 180 / math.pi + 360) % 360)

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y, self.rotation + other.rotation)

    def __sub__(self, other):
        return Position(self.x - other.x, self.y - other.y, self.rotation - other.rotation)

    def __mul__(self, other):
        return Position(self.x * other, self.y * other, self.rotation * other)

    def __truediv__(self, other):
        return Position(self.x / other, self.y / other, self.rotation / other)

    def __getitem__(self, item):
        if item == 2:
            return self.rotation
        else:
            return super().__getitem__(item)

    def __setitem__(self, index, value):
        if index == 2:
            self.rotation = value
        else:
            super().__setitem__(index, value)