import random
from abc import ABC, abstractmethod

import pygame.mask

from Utils.Position import Position
from Utils.AccelerationSmoother import AccelerationSmoother
from Field import Circle
from math import cos, sin, pi
from Utils.DebugPrint import DebugPrint
from Utils.UtilFuncs import sign


class Robot(ABC):
    def __init__(self, starting_position: Position = Position(0, 0), max_acceleration: float = 1000,
                 max_velocity: float = 100, sprite: Circle = Circle(0, 0, 10)):
        self.position = starting_position
        self.velocity = Position(0, 0)
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration
        self.sprite = sprite
        self.trajectory: list[Position] = []

        # integral function = (direction * max_acceleration / 2) * (time_delta^2)
        # for acceleration to stop = max_speed/max_acceleration
        self.critical_duration = self.max_velocity / self.max_acceleration
        self.critical_distance = (self.max_acceleration / 2) * (self.critical_duration ** 2)
        # gives the slope of the function
        self.acceleration_smoother = AccelerationSmoother(self.max_acceleration, max_value=self.max_velocity,
                                                          min_value=0)

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

    def set_trajectory(self, trajectory: list[Position]) -> None:
        """
        Sets the trajectory of the robot
        :param trajectory: The trajectory to set
        :return:
        """
        self.trajectory = trajectory

    def add_waypoint(self, waypoint: Position) -> None:
        """
        Adds a waypoint to the trajectory
        :param waypoint: The waypoint to add
        :return:
        """
        self.trajectory.append(waypoint)

    def follow_trajectory(self, time_delta_seconds: float, trajectory: list[Position] = None, debug=False) -> bool:
        """
        This function makes the robot follow the trajectory
        Edit this function to change how the robot follows the trajectory
        :param time_delta_seconds: The time since the last update
        :param trajectory: The trajectory to follow (if None, uses the current trajectory)
        :param debug: Prints debug statements if true
        :return: If the robot is at the last position in the trajectory
        """
        if trajectory is not None:
            self.set_trajectory(trajectory)

        if len(self.trajectory) > 0:
            if self.go_to_position(self.trajectory[0], time_delta_seconds, debug=debug, update_position=True):
                self.velocity = Position(0, 0)
                self.trajectory.pop(0)  # pops in global scope too

        if len(self.trajectory) == 0:
            return True

    def go_to_position(self, target_position: Position, time_delta_seconds: float, update_position=False,
                       debug=False) -> bool:
        """
        This function makes the robot go to the target position
        Should be overriden depending on what type of robot it is & how you want it to accelerate and deaccelearte
        :param target_position: The position to go to
        :param time_delta_seconds: The time since the last update
        :param debug: Prints debug statements if true
        :return: if the robot is at the target"""

        at_target = False

        # Listen to me, I don't understand how any of this works.
        # I did this by trial and error, just let the black magic do its thing
        target_distance = target_position.get_distance_to(self.position)
        current_magnitude = self.velocity.get_distance_to(Position(0, 0))

        # if within tolerance just set current position to target
        # NOTE: might cause it to have some jittery motion at low fps
        if current_magnitude <= self.max_acceleration * time_delta_seconds and \
                target_distance < time_delta_seconds * (self.max_acceleration - self.acceleration_smoother.get_value()):
            self.acceleration_smoother.set_state(0)
            self.velocity = Position(0, 0)
            current_magnitude = self.velocity.get_distance_to(Position(0, 0)) / time_delta_seconds
            at_target = True

        # handles accelerating down: checks that it is within the "critical distance" of the target
        elif target_distance <= self.calculate_critical_distance():
            current_magnitude = self.acceleration_smoother.update(0, time_delta_seconds)

        # handles accelerating when in critical distance
        else:
            current_magnitude = self.acceleration_smoother.update(self.max_acceleration, time_delta_seconds)

        rotation_to = self.position.get_angle_to(target_position)
        new_velocity = Position(
            cos(rotation_to * pi / 180) * current_magnitude,
            sin(rotation_to * pi / 180) * current_magnitude
        )
        change = new_velocity - self.velocity

        # just for testing
        # simulate sliding, so robot decelerates slower
        # error_func = lambda pos: pos * Position(
        #     (1 if (sign(change.x) == sign(self.velocity.x)) else 0.5),
        #     (1 if (sign(change.y) == sign(self.velocity.y)) else 0.5),
        #     1
        # )

        # DebugPrint.add_debug_function(f"{error_func(change)=}, {change=}, {self.velocity=}")
        self.apply_force(change, time_delta_seconds, limit_acceleration=True, apply_velocity=update_position) #,
                         # error_function=error_func)

        return at_target

    @abstractmethod
    def path_find(self, target_position: Position, debug=False) -> list[Position]:
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
                    apply_velocity: bool = True, error_function=lambda pos: pos * 1) -> None:
        """ This function applies a force to the robot
        :param error_function: Function to add error to the force
        :param force: The force to apply to the robot
        :param time_delta_seconds: The time since the last update
        :param limit_acceleration: If the acceleration should be limited to the robot's max
        :param apply_velocity: If the new velocity should be applied to the robot's position
        :return:
        """
        # adds error to the force
        force = error_function(force)
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
