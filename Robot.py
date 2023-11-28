from abc import ABC, abstractmethod

import pygame.mask

from Position import Position
from Field import Circle, Field
from math import cos, sin, pi


class Robot(ABC):
    def __init__(self, starting_position: Position = Position(0, 0), max_accelerations: Position = Position(100, 100),
                 max_velocity: float = 100, sprite: Circle = Circle(0, 0, 10)):
        self.position = starting_position
        self.velocity = Position(0, 0)
        self.max_velocity = max_velocity
        self.max_accelerations = max_accelerations
        self.sprite = sprite

    def go_to_position(self, target_position: Position, time_delta_seconds: float, debug=False) -> None:
        """
        This function makes the robot go to the target position.
        Should be overriden depending on what type of robot it is & how you want it to accelerate and deaccelearte
        :param target_position: The position to go to
        :param time_delta_seconds: The time since the last update
        :param debug: Prints debug statements if true
        :return:"""
        # force = target_position - (self.position + self.velocity)
        # force.rotation = self.position.rotation
        # self.apply_force(force, time_delta_seconds, limit_acceleration=True)

        if target_position.get_distance_to(self.position) < 2:  # deadzone to prevent jittering

            self.velocity = Position(0, 0)
            return

        rotation_to = self.position.get_angle_to(target_position)

        self.velocity.x = cos(rotation_to * pi / 180) * self.max_velocity
        self.velocity.y = sin(rotation_to * pi / 180) * self.max_velocity

        self.update(time_delta_seconds, debug=debug)

    @abstractmethod
    def path_find(self, target_position: Position, debug=False) -> Position:
        """
        This function should feed the robot positions to go to
        :param target_position: The position to go to
        :param : The time since the last update
        :param debug: If the function should print debug statements
        :return: The position the robot should go to
        """
        pass

    @abstractmethod
    def display(self, screen) -> None:
        """
        This function should display the robot on the screen using pygame
        :param screen:
        :return:
        """
        pass

    def update(self, time_delta_seconds: float, debug=False) -> None:
        """
        This function updates the robot's position based on its current velocity
        :param time_delta_seconds: The time since the last update
        :param debug: Prints position and velocity if true
        :return:
        """
        self.position += self.velocity * time_delta_seconds
        if debug:
            print(f"{self.position=}")
            print(f"{self.velocity=}")

    def apply_force(self, force: Position, time_delta_seconds: float, limit_acceleration: bool = False,
                    apply_velocity: bool = True, debug: bool = False) -> None:
        """ This function applies a force to the robot
        :param debug:
        :param force: The force to apply to the robot
        :param time_delta_seconds: The time since the last update
        :param limit_acceleration: If the acceleration should be limited to the robot's max
        :param apply_velocity: If the new velocity should be applied to the robot's position
        :return:
        """
        # limits acceleration
        if limit_acceleration:
            force.scale_to(self.max_accelerations)

        #   calculates velocity
        self.velocity += force * time_delta_seconds

        #   limits velocity
        self.velocity.scale_to(self.max_velocity, only_downscale=True)

        if apply_velocity:
            self.update(time_delta_seconds, debug=False)

        if debug:
            print(
                '=========================\n'
            )
            print(f"{self.velocity=}")
            print(f"{self.position=}")
            print(f"{force=}")

    def collided_with_mask(self, mask: pygame.mask.Mask, ignore_if: pygame.mask.Mask = None) -> bool:
        """
        This function checks if the robot has collided with the field        :param field:  to check
        :return: If the robot has collided with the field
        """
        a = self.sprite.mask.overlap_area(mask, (-self.position.x + self.sprite.radius, -self.position.y + self.sprite.radius))
        if ignore_if is not None:
            b = self.sprite.mask.overlap_area(ignore_if, (-self.position.x + self.sprite.radius, -self.position.y + self.sprite.radius))
            return a - b > 0
        else:
            return a > 0

    @staticmethod
    def clamp(value, max_value, min_value):
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
