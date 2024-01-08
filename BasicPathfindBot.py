import time

from Robot import Robot
from Utils.Position import Position
import pygame
import Field


class BasicPathfindBot(Robot):
    """
    This robot goes to the target position in a straight line
    """

    def __init__(self, field: Field, max_velocity: float = 500, max_acceleration: float = 1000):
        super().__init__(field, max_velocity=max_velocity, max_acceleration=max_acceleration)
        self.force = Position(0, 0, 0)
        self.path_to_next_point = []

    class Node:
        """A node class for A* Pathfinding"""

        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position: Position = position
            self.g = 0
            self.h = 0
            self.f = 0

        def __eq__(self, other):
            return self.position == other.position

    def follow_trajectory(self, time_delta_seconds: float, trajectory: list[Position] = None, _stall=[0]) -> bool:
        """
        This function moves the robot along the trajectory. It returns true if the robot is at the target position
        :param time_delta_seconds:
        :param trajectory:
        :return:
        """

        if trajectory is None:
            trajectory = self.trajectory
        else:
            self.trajectory = trajectory

        if not trajectory:
            self.velocity = Position(0, 0)
            return True

        # pathfinds to the next point
        if not self.path_to_next_point:
            # handles an invalid target
            if (self.field.mask.get_at((int(trajectory[0].x), int(trajectory[0].y))) or
                    self.field.margin_mask.get_at((int(trajectory[0].x), int(trajectory[0].y)))):  # if target in a wall
                print("Invalid target")
                trajectory.pop(0)
                self.velocity = Position(0, 0)
                return False

            start_time = time.time()
            self.path_to_next_point = self.path_find(trajectory[0], debug=False, loop_between_display=[0, 0],
                                                     resolution=1 / 30)
            end_time = time.time()
            print(f"Pathfinding took {end_time - start_time} seconds")
            print(self.path_to_next_point)
            if self.path_to_next_point[0] is None:
                print("Invalid target")
                trajectory.pop(0)
                self.path_to_next_point = []
                self.velocity = Position(0, 0)
                return False

            _stall[0] = 4
            self.velocity = Position(0, 0)
            self.path_to_next_point.append(trajectory[0])  # accounts for error b/c of resolution

        if _stall[0] > 0:
            _stall[0] -= 1
            return False

        target_position = self.path_to_next_point[0]
        if self.go_to_position(target_position, time_delta_seconds, update_position=True):
            self.path_to_next_point.pop(0)
            if len(self.path_to_next_point) == 0:
                trajectory.pop(0)
                self.velocity = Position(0, 0)

        return False

    def path_find(self,target_position: Position,  curr_position: Position=None, loop_between_display=None, debug=False, display=False, resolution: float = 1) -> [
        Position]:
        """A* pathfinding algorithm
        :param debug: kinda useless
        :param loop_between_display: [loop between display, current loop]. -1 just doesn't display
        :param curr_position: the current position. If none, it'll use the robot's position
        :param target_position: the target position
        :param display: if the pathfinding should display
        :param resolution: how many pixels per foot
        """
        # I stole this off the internet
        # Create start and end node
        print("Pathfinding")
        if loop_between_display is None:
            loop_between_display = [-1, 0]

        if curr_position is None:
            curr_position = self.position

        start_node = self.Node(None, curr_position * resolution)
        start_node.g = start_node.h = start_node.f = 0
        end_node = self.Node(None, target_position * resolution)
        end_node.g = end_node.h = end_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        self.velocity = Position(0, 0)

        # Add the start node
        curr_mask: pygame.mask.Mask = self.field.margin_mask.copy()

        curr_mask = pygame.mask.from_surface(
            pygame.transform.smoothscale(curr_mask.to_surface(unsetcolor=(0, 0, 0, 0), setcolor=(255, 255, 255, 255)),
                                         (resolution * curr_mask.get_size()[0], resolution * curr_mask.get_size()[1])),
        )
        open_list.append(start_node)
        visited: pygame.Surface = pygame.Surface(curr_mask.get_size())
        visited.fill((0, 0, 0))
        print(f"There are {curr_mask.get_size()[0] * curr_mask.get_size()[1]} pixels in the mask")

        # display
        if display:
            pygame.display.set_mode(self.field.image.get_size()).blit(
                pygame.transform.scale(curr_mask.to_surface(), self.field.image.get_size()), (0, 0))
            pygame.display.flip()
            time.sleep(0.5)
        # Loop until you find the end
        while len(open_list) > 0:
            # Get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal
            if current_node == end_node or current_node.position.get_distance_to(end_node.position) < 0.9:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                # offset it by 0.5, because the nodes are currently indexes, so plotting the nodes gives you the
                # top left corner of the node, not the center
                return [(i + Position(0.5, 0.5)) / resolution for i in path[::-1]]  # Return reversed path

            # Generate children
            children = []
            # Adjacent squares
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                # Get node position
                node_position = Position(current_node.position[0] + new_position[0],
                                         current_node.position[1] + new_position[1])

                # Make sure within range (inverted)
                if node_position.y > (curr_mask.get_size()[1] - 1) or node_position.y < 0 or node_position.x > (
                        curr_mask.get_size()[0] - 1) or node_position.x < 0:
                    continue
                # Make sure walkable terrain
                if curr_mask.get_at((node_position.x, node_position.y)) or (
                        curr_mask and curr_mask.get_at((node_position.x, node_position.y))):
                    continue
                # Make sure not visited
                if visited.get_at((int(node_position.x), int(node_position.y))) != (0, 0, 0):
                    continue

                # set visited
                visited.set_at((int(node_position.x), int(node_position.y)), (255, 0, 0))

                # display stuff
                if display:
                    if loop_between_display[1] == 0 and loop_between_display[0] >= 0:
                        loop_between_display[1] = loop_between_display[0]
                        pygame.display.set_mode(self.field.image.get_size()).blit(
                            pygame.transform.scale(visited, self.field.image.get_size()), (0, 0))
                        pygame.display.flip()
                        time.sleep(0.02)
                    else:
                        loop_between_display[1] -= 1

                # Create new node
                new_node = self.Node(current_node, node_position)
                # Append
                children.append(new_node)

            # Loop through children
            for child in children:
                # Child is on the closed list
                for closed_child in closed_list:
                    if child == closed_child:
                        continue

                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - end_node.position[0]) ** 2) + (
                        (child.position[1] - end_node.position[1]) ** 2)
                child.f = child.g + child.h

                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # Add the child to the open list
                open_list.append(child)
        return [None]

    def go_to_position(self, target_position: Position, time_delta_seconds: float, update_position=False,
                       slowdown=True) -> bool:
        """
        This function moves the robot to the target position. For this bot it'll be much simpler, as this bot is a proof of concept
        :param target_position:
        :param time_delta_seconds:
        :param update_position:
        :param slowdown:
        :return:
        """
        # helps correct for errors at extremely low FPS
        if self.position.get_distance_to(target_position) < time_delta_seconds * self.max_velocity:
            return True
        # calculates the vector to the target
        vector_to_target = target_position - self.position
        vector_to_target.scale_to(self.max_velocity)
        self.velocity = vector_to_target
        if update_position:
            self.update(time_delta_seconds, debug=False)

        return self.position.get_distance_to(target_position) < time_delta_seconds * self.max_velocity

    def display(self, screen, show_velocity=False) -> None:
        self.sprite.move_to(self.position.x, self.position.y)
        self.sprite.draw(screen)

        # Line to show velocity
        if show_velocity:
            pygame.draw.line(screen, (0, 0, 255), (self.position.x, self.position.y),
                             (self.position.x + self.velocity.x, self.position.y + self.velocity.y), 5)
