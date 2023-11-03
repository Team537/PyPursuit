import time

from Position import Translation, Position
from AccelerationSmoother import AccelerationSmoother, sign, get_current_time
import math

from Rotation import Rotation


class Robot:
    def __init__(self, starting_position: Position = Position(0, 0),
                 max_accelerations: Position = Position(100, 100, 100),
                 max_velocity: float = 100):
        self.position = starting_position
        self.velocity = Position(0, 0, 0)
        self.max_accelerations = max_accelerations  # the fastest the robot cna accelearte (rotation doens't do anythin)
        self.max_velocity = max_velocity  # the heighest speed the robot can go
        self.last_update_time = 0
        self._magnitude_smoother = AccelerationSmoother(
            Position(0, 0, 0).get_distance_to(self.max_accelerations),
            initial_value=self.position.get_distance_to(starting_position),
            max_value=max_velocity,
            min_value=0
        )
        self._rotation_smoother = AccelerationSmoother(
            self.max_accelerations[2], initial_value=self.position[2]
        )

    def go_to_position(self, target_position: Position, debug=False, time_difference=None):
        if time_difference is None:
            current_updated_time = get_current_time()
            time_difference = current_updated_time - self.last_update_time
            self.last_update_time = current_updated_time
        else:
            self.last_update_time += time_difference

        # calculate targets
        target_magnitude = self.position.get_distance_to(target_position)
        target_rotation = Rotation(self.position.get_angle_to(target_position))
        if debug:
            print(f"{target_magnitude=}\n{target_rotation=}\n")

        #   calculate speed
        magnitude = self._magnitude_smoother.update(current_target=target_magnitude, print_debug=debug,
                                                    time_difference=time_difference)
        rotation = self._rotation_smoother.update(current_target=target_rotation, print_debug=debug,
                                                  time_difference=time_difference)
        self.position[2] = rotation

        #   calculate velocity
        self.velocity.x = math.cos(rotation * math.pi / 180) * magnitude
        self.velocity.y = math.sin(rotation * math.pi / 180) * magnitude

        if debug:
            print(f"{rotation=}\n{magnitude=}\n{self.velocity=}\n")

        #   calculate position
        self.position.x += self.velocity.x * time_difference
        self.position.y += self.velocity.y * time_difference

        #   check if we are at the target
        # if sign(target_position.x - self.position.x) != sign(self.velocity.x):
        #     self.velocity.x = 0
        #     self.position.x = target_position.x

        #         if sign(target_position.y - self.position.y) != sign(self.velocity.y):
        #             self.velocity.y = 0
        #             self.position.y = target_position.y

        #   return speed
        return self.velocity

    def display(self, pygame, screen, body_color=0x00FF00, target_color=0x000FF):
        pygame.draw.circle(
            screen, body_color,
            (int(self.position.x), int(self.position.y)),
            10
        )

        pygame.draw.line(screen, target_color, (self.position[0], self.position[1]), (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1]),
                         5
                         )
