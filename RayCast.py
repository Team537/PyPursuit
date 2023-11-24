from pygame.mask import Mask
from Position import Position
from math import ceil


def ray_cast(start: Position, end: Position, mask: Mask, return_point: bool = False) -> bool | Position:
    """
    This function casts a ray from the start position to the end position and returns if it hit the mask
    :param start: The start position
    :param end: The end position
    :param mask: The mask to check
    :return: If the ray hit the mask
    """

    #   calculates the distance between the start and end
    distance = start.get_distance_to(end)
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

        #   checks if the current position is colliding with the mask
        if mask.get_at((int(current_position.x), int(current_position.y))):
            #   returns true if it is
            if return_point:
                return current_position
            return True

    #   returns false if it isn't
    return False
