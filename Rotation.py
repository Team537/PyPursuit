class Rotation(float):
    @staticmethod
    def distance_to(a, b):
        return Rotation((float(a) - float(b) + 180) % 360 - 180)

    def __add__(self, other):
        return Rotation((float(self) + float(other) + 3600) % 360)

    def __sub__(self, other):
        return self.distance_to(self, other)
