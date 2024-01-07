import math

from pygame.mask import Mask
from Field import Field
import pygame
from math import atan2, pi
from time import time
import pickle
from Utils.DebugPrint import DebugPrint

from Utils.RayCast import ray_cast
from Utils.Position import Position


class Edge:
    def __init__(self, next_point: Position, weight: float = 1):
        self.next_point = next_point
        self.weight = weight


class SIGNavMesh:
    """
    This class represents a superimposed grid navigation mesh. The general idea is to generate a grid of points, mask
    it, hollow it out, remove collinear points, and then triangulate the remaining points.
    """

    def __init__(self, field_mask: Mask):
        self.polygon_point_outlines = []
        self.field_mask = field_mask
        self.points = []
        self.graph: dict[Position, list[Edge]] = dict()


    def mesh_baker(self) -> list[tuple[float, float, float]]:
        """
        "Best Bakery in town"
        This function triangulates the nav mesh
        :return:
        """
        all_points = []
        for polygon_points in self.polygon_point_outlines:
            all_points += polygon_points

        print(f"Baking {len(all_points)} points")
        print(f"Estimated time: {len(all_points) ** 2 / 8000} seconds")
        start_time = time()
        lines = 0
        for node in all_points:
            for other_node in all_points:
                # print(f"Ray casting from {node} to {other_node}")
                if node != other_node:
                    if not ray_cast(Position(node[0], node[1]), Position(other_node[0], other_node[1]), self.field_mask):
                        lines += 1
                        self.graph[Position(node[0], node[1])].append(
                            Edge(
                                Position(other_node[0], other_node[1]),
                                weight=Position(node[0], node[1]).get_distance_to(Position(other_node[0], other_node[1]))
                            )
                        )

        print(f"Time taken: {time() - start_time}")
        print(f"Lines: {lines}")

        return None

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
            for point in results:
                self.graph[Position(point[0], point[1])] = []
            self.polygon_point_outlines.append(results)

        DebugPrint.add_debug_function(f"There are {len(self.polygon_point_outlines)} polygons with a threshold of {threshold}")
        DebugPrint.add_debug_function(f"There are {total_outline} total points")
        DebugPrint.add_debug_function(f"Time taken: {time() - start_time}")

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

        DebugPrint.add_debug_function(f"Added {len(points) - start_size} corners")

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
        if threshold_degrees == 180:
            return True
        angle1 = atan2(point1[1] - point2[1], point1[0] - point2[0])
        angle2 = atan2(point2[1] - point3[1], point2[0] - point3[0])
        return (abs(angle1 - angle2) * 180 / pi) % 180 <= threshold_degrees % 180

    def save_graph(self, filename: str) -> None:
        """
        This function saves the nav mesh to a file
        :param filename: The name of the file to save to
        :return:
        """
        with open(filename, "wb") as fout:
            pickle.dump((self.points, self.graph), fout)

    def load_graph(self, filename: str) -> None:
        """
        This function loads the nav mesh from a file
        :param filename: The name of the file to load from
        :return:
        """
        with open(filename, "rb") as fin:
            self.points, self.graph = pickle.load(fin)


if __name__ == "__main__":
    pygame.init()
    # so that pygame doesn't error out
    screen = pygame.display.set_mode((1, 1))

    load_from_file = False
    test_mesh = SIGNavMesh(
        Field(
            pygame.image.load("images/Please don't crash my pc this time.png"), margin=4, margin_shape="square"
        ).margin_mask
    )

    if load_from_file:
        # placeholder
        try:
            print("Loading nav mesh")
            test_mesh.load_graph("nav_meshes/TestNavMesh.pickle")
            print("Loaded nav mesh")
        except FileNotFoundError:
            print("======Warning=======\nNav mesh not found, generating new one\n====================")
            load_from_file = False

    if not load_from_file:
        test_mesh.generate_nodes()
        print("Started Baking")
        test_mesh.mesh_baker()
        print("Finished Baking")
        test_mesh.save_graph("nav_meshes/TestNavMesh.pickle")

    screen = pygame.display.set_mode(test_mesh.field_mask.get_size())
    pygame.display.set_caption(f"Nav Mesh Test")

    image = pygame.Surface(test_mesh.field_mask.get_size())
    image.blit(test_mesh.field_mask.to_surface(), (0, 0))


    for polygon_points in test_mesh.polygon_point_outlines:
        for point in polygon_points:
            image.set_at(point, (255, 0, 0))

    color_change = (max(screen.get_size()) / 6)  # the constant means what ratio it takes to change to red
    for point in test_mesh.graph:
        for edge in test_mesh.graph[point]:
            pygame.draw.line(image,
                 (
                    255 - math.floor(255 / math.ceil(edge.weight / color_change)),
                    255 / math.floor(math.ceil(edge.weight / color_change)), 0
                 ),
                 point.as_tuple()[:2], edge.next_point.as_tuple()[:2]
             )

    pygame.image.save(image, "images/NavMesh.png")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(image, (0, 0))

        pygame.display.flip()
