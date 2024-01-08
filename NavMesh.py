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


class TriangleNavMesh:
    """
    This class represents a superimposed grid navigation mesh. The general idea is to generate a grid of points, mask
    it, hollow it out, remove collinear points, and then triangulate the remaining points.
    """

    def __init__(self, pixels_per_foot):
        self.pixels_per_foot = pixels_per_foot
        self.triangles: list[tuple[Position, Position, Position]] = []  # 3 points
        self.points: list[Position] = []
        self.graph: list[list[int]] = []

    def create_surface(self, size: tuple[int, int] = (1000, 1000), point_color=(0, 255, 0, 255),
                       line_color=(255, 0, 0, 255)) -> pygame.Surface:
        """
        This function displays the nav mesh on the given surface
        :param screen: The surface to draw to
        :param field: The field to draw on
        :param color: The color to draw the mesh in
        :return:
        """
        screen = pygame.Surface(size, pygame.SRCALPHA)
        screen.fill((0, 0, 0, 0))
        for triangle in self.triangles:
            pygame.draw.line(screen, line_color, (self.points[triangle[0]] * self.pixels_per_foot).as_tuple()[:2],
                             (self.points[triangle[1]] * self.pixels_per_foot).as_tuple()[:2], 2)
            pygame.draw.line(screen, line_color, (self.points[triangle[1]] * self.pixels_per_foot).as_tuple()[:2],
                             (self.points[triangle[2]] * self.pixels_per_foot).as_tuple()[:2], 2)
            pygame.draw.line(screen, line_color, (self.points[triangle[2]] * self.pixels_per_foot).as_tuple()[:2],
                             (self.points[triangle[0]] * self.pixels_per_foot).as_tuple()[:2], 2)

        for points in self.points:
            pygame.draw.circle(screen, point_color, (points * self.pixels_per_foot).as_tuple()[:2], 3)
        return screen

    def manually_make_nodes(self, image: pygame.Surface, scale=3) -> None:
        """
        This function generates the nodes for the nav mesh
        :param pixels_per_foot:
        :param node_map: a map with all the nodes as opaque (a = 255) pixels
        :return:
        """
        screen = pygame.display.set_mode((image.get_width() * scale, image.get_height() * scale))
        pygame.display.set_caption(f"Mannual Node Maker")

        self.points = set()
        stage = 0

        running = True
        last_line_point = None
        curr_triangle = []
        curr_triangles: list[tuple[Position, Position, Position]] = []
        last_mouse_state = pygame.mouse.get_pressed()
        font = pygame.font.Font('freesansbold.ttf', 32)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((255, 255, 255))
            screen.blit(pygame.transform.scale(image, (screen.get_width(), screen.get_height())), (0, 0))
            mouse_x, mouse_y = pygame.mouse.get_pos()
            curr_point = None

            for point in self.points:
                pygame.draw.circle(screen, (0, 255, 0), (point * self.pixels_per_foot).as_tuple()[:2], 3)
                if Position(mouse_x, mouse_y).get_distance_to(point * self.pixels_per_foot) < 3:
                    curr_point = point
                    pygame.draw.circle(screen, (255, 0, 0), (point * self.pixels_per_foot).as_tuple()[:2], 3)

            # Triangles
            for triangle in curr_triangles:
                pygame.draw.line(screen, (0, 0, 255), triangle[0].as_tuple()[:2],
                                 triangle[1].as_tuple()[:2], 2)
                pygame.draw.line(screen, (0, 0, 255), triangle[1].as_tuple()[:2],
                                 triangle[2].as_tuple()[:2], 2)
                pygame.draw.line(screen, (0, 0, 255), triangle[2].as_tuple()[:2],
                                 triangle[0].as_tuple()[:2], 2)

            for i in range(1, len(curr_triangle)):
                print(curr_triangle[i-1] * self.pixels_per_foot, curr_triangle[i] * self.pixels_per_foot)
                pygame.draw.line(screen, (0, 255, 0), tuple(map(int, (curr_triangle[i - 1] * self.pixels_per_foot).as_tuple()[:2])),
                                 tuple(map(int, (curr_triangle[i] * self.pixels_per_foot).as_tuple()[:2])), 2)

            if stage == 0:  # add points
                screen.blit(font.render("Click to add/delete points (right click to continue)", True, (255, 0, 0)),
                            (5, 5))
                if pygame.mouse.get_pressed()[0] and not last_mouse_state[0]:
                    if curr_point is None:
                        self.points.add(Position(mouse_x, mouse_y) / self.pixels_per_foot)
                    else:
                        self.points.remove(curr_point)

                if pygame.mouse.get_pressed()[2] and not last_mouse_state[2]:
                    stage = 1

            elif stage == 1:  # add edges
                screen.blit(font.render("Click to add lines (right click to continue)", True, (255, 0, 0)), (5, 5))
                if last_line_point:
                    pygame.draw.line(screen, (0, 0, 255), (last_line_point * self.pixels_per_foot).as_tuple()[:2],
                                     (Position(mouse_x, mouse_y)).as_tuple()[:2], 2)

                if pygame.mouse.get_pressed()[0] and not last_mouse_state[0]:
                    if curr_point is not None:
                        if last_line_point is None:
                            last_line_point = curr_point
                        else:
                            if len(curr_triangle) == 0:
                                curr_triangle.append(last_line_point)
                            curr_triangle.append(curr_point)
                            last_line_point = curr_point
                            if len(curr_triangle) == 3:
                                curr_triangles.append(tuple(curr_triangle))
                                curr_triangle = []

            last_mouse_state = pygame.mouse.get_pressed()
            pygame.display.flip()

    def load_graph(self, filename: str) -> None:
        """
        This function loads the nav mesh from a file
        :param filename: The name of the file to load from
        :return:
        """
        if not filename.endswith(".trinavmesh"):
            raise ValueError("File must be a .navmesh file")
        with open(filename, "r") as fin:
            point_count, triangle_count, edge_count = map(int, fin.readline().split(" "))
            self.points = [Position(float(i[0]), float(i[2])) for i in fin.readline().split(" ")]
            self.triangles = [tuple(map(int, fin.readline().split(" "))) for _ in range(triangle_count)]
            self.graph = [list() for _ in range(triangle_count)]
            for _ in range(edge_count):
                a, b = map(int, fin.readline().split(" "))
                self.graph[a].append(b)


if __name__ == "__main__":
    pygame.init()
    # so that pygame doesn't error out
    screen = pygame.display.set_mode((1000, 1000))

    load_from_file = False
    test_mesh = TriangleNavMesh(pixels_per_foot=300)
    if load_from_file:
        test_mesh.load_graph("nav_meshes/test.trinavmesh")
    else:
        test_mesh.manually_make_nodes(pygame.image.load("images/Map.png"))
    #
    # pygame.display.set_caption(f"Nav Mesh Test")
    # image = test_mesh.create_surface(size=(1000, 1000))
    #
    # running = True
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False
    #     screen.fill((255, 255, 255))
    #     screen.blit(image, (0, 0))
    #     pygame.display.flip()
