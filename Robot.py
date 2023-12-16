from abc import ABC, abstractmethod

import pygame.mask

from Utils.Position import Position
from Utils.AccelerationSmoother import AccelerationSmoother, sign
from Field import Circle
from math import cos, sin, pi
from Utils.DebugPrint import DebugPrint
from Utils.DebugPrint import DebugPrint

class Robot(ABC):
    def __init__(self, starting_position: Position = Position(0, 0), max_acceleration: float = 1000,
                 max_velocity: float = 100, sprite: Circle = Circle(0, 0, 10)):
        self.position = starting_position
        self.velocity = Position(0, 0)
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration
        self.sprite = sprite

        # integral function = (direction * max_acceleration / 2) * (time_delta^2)
        # for acceleration to stop = max_speed/max_acceleration
        self.critical_duration = self.max_velocity / self.max_acceleration
        self.critical_distance = (self.max_acceleration / 2) * (self.critical_duration ** 2)
        # gives the slope of the function
        self.acceleration_smoother = AccelerationSmoother(self.max_acceleration, max_value=self.max_velocity, min_value=-self.max_velocity)
        self.state = 0

    def calculate_critical_distance(self) -> float:
        """
        Calculates the distance needed to go from the current speed to 0 acceleration
        """
        current_acceleration = self.acceleration_smoother.get_value()

        # gets the duration till the derivative is at 0
        critical_duration = current_acceleration / self.max_acceleration
        critical_distance = (self.max_acceleration / 2) * abs(
                critical_duration ** 2)  # integral calculation should stay the same
        return critical_distance

    def go_to_position(self, target_position: Position, time_delta_seconds: float, debug=False) -> None:
        """
        This function makes the robot go to the target position
        Should be overriden depending on what type of robot it is & how you want it to accelerate and deaccelearte
        :param target_position: The position to go to
        :param time_delta_seconds: The time since the last update
        :param debug: Prints debug statements if true
        :return:"""

        # Listen to me, I don't understand how any of this works.
        # I did this by trial and error, just let the black magic do its thing
        target_distance = target_position.get_distance_to(self.position)
        current_magnitude = self.velocity.get_distance_to(Position(0, 0))

        state = 0
        # if within tolerance just set current position to target
        # NOTE: might cause it to have some jittery motion at low fps
        if self.acceleration_smoother.get_value() == 0 and \
                target_distance < time_delta_seconds * self.max_acceleration:
            self.position = target_position
            self.acceleration_smoother.set_state(0)

        # handles accelerating down: checks that it is within the "critical distance" of the target
        elif target_distance <= self.calculate_critical_distance():
            current_magnitude = self.acceleration_smoother.update(0, time_delta_seconds)
            state = -1

        # handles accelerating when in critical distance
        else:
            current_magnitude = self.acceleration_smoother.update(self.max_acceleration, time_delta_seconds)
            state = 1

        rotation_to = self.position.get_angle_to(target_position)
        new_velocity = Position(
            cos(rotation_to * pi / 180) * current_magnitude,
            sin(rotation_to * pi / 180) * current_magnitude
        )

        change = new_velocity - self.velocity
        self.apply_force(change, time_delta_seconds, debug=debug, limit_acceleration=True, apply_velocity=False)

        DebugPrint.add_debug_function(lambda : print(f"{target_distance=}"))
        DebugPrint.add_debug_function(lambda : print(f"{current_magnitude=}"))
        DebugPrint.add_debug_function(lambda : print(f"{self.calculate_critical_distance()=}"))
        DebugPrint.add_debug_function(lambda : print(f"{self.acceleration_smoother.get_value()=}"))
        DebugPrint.add_debug_function(lambda : print(f"{state=}"))
        DebugPrint.add_debug_function(lambda : print(f"{change=}"))
        self.state = state

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
            DebugPrint.add_debug_function(f"{self.position=}")
            DebugPrint.add_debug_function(f"{self.velocity=}")

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
            force.scale_to(self.max_acceleration, only_downscale=True)

        #   calculates velocity
        self.velocity += force

        #   limits velocity
        self.velocity.scale_to(self.max_velocity, only_downscale=True)

        if apply_velocity:
            self.update(time_delta_seconds, debug=False)

    def collided_with_mask(self, mask: pygame.mask.Mask) -> bool:
        """
        This function checks if the robot has collided with the field        :param field:  to check
        :return: If the robot has collided with the field
        """
        return self.sprite.mask.overlap_area(mask, (
            -self.position.x + self.sprite.radius, -self.position.y + self.sprite.radius)) > 0

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
