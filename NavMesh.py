from pygame.mask import Mask
from Field import Field
import pygame
from math import atan2, pi
from time import time
import pickle

class SIGNavMesh:
    """
    This class represents a superimposed grid navigation mesh. The general idea is to generate a grid of points, mask
    it, hollow it out, remove collinear points, and then triangulate the remaining points.
    """

    def __init__(self, field_mask: Mask):
        self.points = []
        self.lines = []
        self.field_mask = field_mask
        self.inverse_mask = field_mask.copy()
        self.inverse_mask.invert()

    def generate_nodes(self, threshold: float = 0) -> None:
        """
        This function generates the nodes for the nav mesh
        :param threshold: The threshold for the collinear function
        :return:
        """

        start_time = time()
        # generates the outline of the traversable area, and gets rid of straight edges
        components = self.field_mask.connected_components()
        total_outline = 0
        for component in components:
            outline = component.outline()
            total_outline += len(outline)
            results = self.linearize(outline, threshold)
            self.points += results

        print(f"There are {len(components)} components")
        print(f"There are {len(self.points)} collinear points with a threshold of {threshold}")
        print(f"There are {total_outline} total points")
        print(f"Removed {total_outline - len(self.points)} collinear points")
        print(f"Time taken: {time() - start_time}")

    def linearize(self, points: list | tuple, threshold) -> list[int, int]:
        """
        This function removes roughly collinear points from the nav mesh
        :param points: The points to linearize
        :param threshold: The threshold for the collinear function (0 is exact)
        :return:
        """
        # compensate for the fact that the first and last points are skipoped
        points += points[0:1]

        # adds corners to the list of points
        offset = 1
        start_size = len(points)
        # goes through each point
        for current_point_i in range(len(points) - 1):
            # checks if the points are diagonal
            if self.is_diagonal(points[current_point_i], points[current_point_i + 1]):
                current_point = points[current_point_i]
                next_point = points[current_point_i + 1]

                # checks the four points around the current point
                for i in (1, -1, 0, 0):
                    stop = False # if the corner has been found
                    for j in (0, 0, 1, -1):
                        # checks if the point is in the field
                        if self.field_mask.get_at((current_point[0] + i, current_point[1] + j)):
                            # make sure the corner is touching the next point
                            if (current_point[0] + i - next_point[0]) ** 2 + (
                                    current_point[1] + j - next_point[1]) ** 2 == 1:
                                points.insert(current_point_i + offset,
                                                   (current_point[0] + i, current_point[1] + j))
                                offset += 1
                                stop = True
                                break
                    if stop:
                        break

        print(f"Added {len(points) - start_size} corners")

        # removes collinear points ADDITION METHOD
        remaining_points = []
        for current_point in range(len(points) - 2):
            if not self.collinear(points[current_point], points[current_point + 1],
                                  points[current_point + 2],
                                  threshold_degrees=threshold):
                remaining_points.append(points[current_point + 1])

        return remaining_points

    @staticmethod
    def is_diagonal(point1: tuple[int, int], point2: tuple[int, int]) -> bool:
        """
        This function checks if two points are diagnol
        :param point1: The first point
        :param point2: The second point
        :return: If the two points are diagnol
        """
        return abs(point1[0] - point2[0]) == 1 and abs(point1[1] - point2[1]) == 1

    @staticmethod
    def collinear(point1: tuple[int, int], point2: tuple[int, int], point3: tuple[int, int],
                  threshold_degrees: float = 0) -> bool:
        """
        This function checks if three points are collinear.
        :param point1: The first point
        :param point2: The second point
        :param point3: The third point
        :param threshold_degrees: The threshold for the collinear function (0 is exact, 180 is always true)
        :return: If the three points are collinear
        """
        # #  calculates the area of a triangle formed by the three points
        # area_of_triangle = abs((point1[0] * (point2[1] - point3[1]) + point2[0] * (point3[1] - point1[1]) +
        #                         point3[0] * (point1[1] - point2[1])) / 2.0)
        # a point is collinear if the area of the triangle formed by the three points is 0, however the threshold
        # allows for some error
        if threshold_degrees == 180:
            return True
        angle1 = atan2(point1[1] - point2[1], point1[0] - point2[0])
        angle2 = atan2(point2[1] - point3[1], point2[0] - point3[0])
        return (abs(angle1 - angle2) * 180 / pi) % 180 <= threshold_degrees % 180

    def save(self, filename: str) -> None:
        """
        This function saves the nav mesh to a file
        :param filename: The name of the file to save to
        :return:
        """
        with open(filename, "wb") as fout:
            pickle.dump(self.points, fout)

    def load(self, filename: str) -> None:
        """
        This function loads the nav mesh from a file
        :param filename: The name of the file to load from
        :return:
        """
        with open(filename, "rb") as fin:
            self.points = pickle.load(fin)


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption(f"Nav Mesh Test")

    test_mesh = SIGNavMesh(
        Field(pygame.image.load("images/TestField.png"), margin=4, margin_shape="square").margin_mask)

    reset = True

    if not reset:
        try:
            pass
            # test_mesh.load("nav_meshes/TestNavMesh.pickle")
        except FileNotFoundError:
            test_mesh.generate_nodes()
            test_mesh.save("nav_meshes/TestNavMesh.pickle")
    else:
        test_mesh.generate_nodes()
        test_mesh.save("nav_meshes/TestNavMesh.pickle")

    image = pygame.Surface((1000, 1000))
    image.blit(test_mesh.field_mask.to_surface(), (0, 0))

    for point in test_mesh.points:
        image.set_at(point, (255, 0, 0))

    pygame.image.save(image, "images/NavMesh.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(image, (0, 0))

        pygame.display.flip()
