from pygame.mask import Mask
from Utils.Position import Position
from math import ceil


def ray_cast(start: Position, end: Position, mask: Mask, return_point: bool = False, tolerance: float = 1.4) -> bool | Position:
    """
    This function casts a ray from the start position to the end position and returns true if it hit the mask
    :param start: The start position
    :param end: The end position
    :param mask: The mask to check
    :param return_point: If the function should return the point of collision
    :return: If the ray hit the mask
    """

    #   calculates the distance between the start and end
    distance = start.get_distance_to(end)
    if distance == 0:
        return False

    translation = (end - start)

    #   calculates the step size
    step_size = translation / distance

    #   calculates the number of steps
    steps = distance / step_size.get_distance_to(Position(0, 0))

    #   creates a variable to track the current position of the ray
    current_position = start

    #   loops through each step
    for _ in range(ceil(steps)):
        #   moves the current position
        current_position += step_size

        #   check if the current position is out of bounds
        if not (0 <= current_position.x < mask.get_size()[0] and 0 <= current_position.y < mask.get_size()[1]):
            #   returns false if it isn't
            return False

        #   checks if the current position is colliding with the mask
        pos = (round(current_position.x), round(current_position.y))
        if mask.get_at(pos):
            if current_position.get_distance_to(end) < tolerance:
                return False
            #   returns true if it is
            if return_point:
                return current_position
            return True

    #   returns false if it isn't
    return False
