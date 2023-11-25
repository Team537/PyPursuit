from pygame.mask import Mask
from Field import Field
import pygame
from math import atan2, pi
from time import time


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

    def generate_nodes(self, threshold: float = 30) -> None:
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
            self.points += self.linearize(outline, threshold=threshold)

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

        # removes collinear points ADDITION METHOD
        remaining_points = []
        for current_point in range(len(points) - 2):
            if current_point < len(points) - 2 and not self.collinear(points[current_point], points[current_point + 1],
                                                                      points[current_point + 2],
                                                                      threshold_degrees=threshold):
                remaining_points.append(points[current_point + 1])

        return remaining_points

    @staticmethod
    def collinear(point1: tuple[int, int], point2: tuple[int, int], point3: tuple[int, int],
                  threshold_degrees: float = 0) -> bool:
        """
        This function checks if three points are collinear.
        :param point1: The first point
        :param point2: The second point
        :param point3: The third point
        :param threshold_degrees: The threshold for the collinear function (0 is exact)
        :return: If the three points are collinear
        """
        # #  calculates the area of a triangle formed by the three points
        # area_of_triangle = abs((point1[0] * (point2[1] - point3[1]) + point2[0] * (point3[1] - point1[1]) +
        #                         point3[0] * (point1[1] - point2[1])) / 2.0)
        # a point is collinear if the area of the triangle formed by the three points is 0, however the threshold
        # allows for some error
        angle1 = atan2(point1[1] - point2[1], point1[0] - point2[0])
        angle2 = atan2(point2[1] - point3[1], point2[0] - point3[0])
        return (abs(angle1 - angle2) * 180/pi) % 180 <= threshold_degrees % 180

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption(f"Nav Mesh Test")

    test_mesh = SIGNavMesh(Field(pygame.image.load("images/TestField.png"), margin=4, margin_shape="square").margin_mask)
    test_mesh.generate_nodes()

    image = pygame.Surface((1000, 1000))
    image.blit(test_mesh.field_mask.to_surface(), (0, 0))

    for point in test_mesh.points:
        pygame.draw.circle(image, (255, 0, 0), point, 1)

    pygame.image.save(image, "images/NavMesh.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(image, (0, 0))

        pygame.display.flip()
