import math
from Rotation import Rotation
from Translation import Translation


class Position(Translation):
    """A Translation with a rotation
    x and y are the position of the center of the robot, rotation is the rotation of the robot in degrees"""

    def __init__(self, x, y, rotation: float | Rotation = Rotation(0)):
        super().__init__(x, y)
        self.rotation = Rotation(rotation)  # in degrees

    def get_rotation_difference(self, other):
        return Rotation.distance_to(self.rotation, other.rotation)

    def get_angle_to(self, other):
        return Rotation((math.atan2(other.y - self.y, other.x - self.x) * 180 / math.pi + 360) % 360)

    def as_positive(self):
        return Position(abs(self.x), abs(self.y), self.rotation)

    def as_list(self):
        return [self.x, self.y, self.rotation]

    def scale_to(self, scale: "Position | float | int", only_downscale=False):
        if isinstance(scale, Position):
            other = scale.as_positive()
            this = self.as_positive() + Position(0.0000001, 0.0000001, 0.0000001)
            scale = min(other.as_list()[:2]) / max(this.as_list()[:2])
        elif isinstance(scale, float) or isinstance(scale, int):
            scale = scale / self.get_distance_to(Position(0, 0))
        else:
            raise TypeError(f"scale must be a Position, float, or int, not {type(scale)}")

        if only_downscale:
            scale = min(scale, 1)
        self.x *= scale
        self.y *= scale
        self.rotation *= scale
        return self
    
    # bunch of operator overloads

    def __repr__(self):
        return f"Position({self.x}, {self.y}, {self.rotation})"

    def __add__(self, other: "float | int | Position"):
        if isinstance(other, float) or isinstance(other, int):
            return Position(self.x + other, self.y + other, self.rotation + other)
        elif isinstance(other, Position):
            return Position(self.x + other.x, self.y + other.y, self.rotation + other.rotation)
        else:
            raise TypeError(f"other must be a float, int, or Position, not {type(other)}")

    def __sub__(self, other: "float | int | Position"):
        if isinstance(other, float) or isinstance(other, int):
            return Position(self.x - other, self.y - other, self.rotation - other)
        elif isinstance(other, Position):
            return Position(self.x - other.x, self.y - other.y, self.rotation - other.rotation)
        else:
            raise TypeError(f"other must be a float, int, or Position, not {type(other)}")

    def __mul__(self, other: "float | int | Position"):
        if isinstance(other, float) or isinstance(other, int):
            return Position(self.x * other, self.y * other, self.rotation * other)
        elif isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y, self.rotation * other.rotation)
        else:
            raise TypeError(f"other must be a float, int, or Position, not {type(other)}")

    def __truediv__(self, other: "float | int | Position"):
        if isinstance(other, float) or isinstance(other, int):
            return Position(self.x / other, self.y / other, self.rotation / other)
        elif isinstance(other, Position):
            return Position(self.x / other.x, self.y / other.y, self.rotation / other.rotation)
        else:
            raise TypeError(f"other must be a float, int, or Position, not {type(other)}")

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
