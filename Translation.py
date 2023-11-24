import math


class Translation:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def as_list(self):
        return [self.x, self.y]

    def __add__(self, other):
        return Translation(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Translation(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Translation(self.x * other, self.y * other)

    def __truediv__(self, other):
        return Translation(self.x / other, self.y / other)

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.x, self.y))

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError(f"Index {index} out of range for Translation")

    def __setitem__(self, index, value):
        if index == 0:
            self.x = value
        elif index == 1:
            self.y = value
        else:
            raise IndexError(f"Index {index} out of range for Translation")
