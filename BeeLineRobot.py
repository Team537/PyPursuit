from Robot import Robot
from Position import Position
import pygame


class BeeLineRobot(Robot):
    """
    This robot goes to the target position in a straight line
    """

    def __init__(self, max_accelerations: Position = Position(100, 100, 100), max_velocity: float = 100):
        super().__init__(max_velocity=max_velocity, max_accelerations=max_accelerations)
        self.force = Position(0, 0, 0)

    def path_find(self, target_position: Position, debug=False) -> Position:
        # just go straight to the target
        return target_position

    def display(self, screen, show_velocity=False) -> None:
        self.sprite.move_to(self.position.x, self.position.y)
        self.sprite.draw(screen)

        # Line to show velocity
        if show_velocity:
            pygame.draw.line(screen, (0, 0, 255), (self.position.x, self.position.y),
                         (self.position.x + self.velocity.x, self.position.y + self.velocity.y), 5)

