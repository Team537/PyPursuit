import math
import os
import time

import pygame

from Robot import Robot
from Position import Position

last_time = time.time_ns() / 1e9
def every_delay(delay):
    global last_time
    if time.time_ns() / 1e9 - last_time >= delay:
        last_time = time.time_ns() / 1e9
        return True
    return False

pygame.init()

screen = pygame.display.set_mode((1000, 1000))
pygame.display.set_caption(f"Robot Test")

font = pygame.font.Font('freesansbold.ttf', 32)

scale = 0.6

robot = Robot(
    Position(screen.get_size()[0] / 2, screen.get_size()[1] / 2),
    max_accelerations=Position(100 * scale, 100 * scale, 1000),
    max_velocity=250 * scale
)

scale = 0.4
robot2 = Robot(
    Position(screen.get_size()[0] / 2, screen.get_size()[1] / 2),
    max_accelerations=Position(100 * scale, 100 * scale, 100),
    max_velocity=250 * scale
)

running = True

FPS = 120

time_scale = 10

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse_x, mouse_y = pygame.mouse.get_pos()

    robot.go_to_position(Position(mouse_x, mouse_y), time_difference=1/FPS * time_scale)
    robot2.go_to_position(Position(mouse_x, mouse_y), time_difference=1/FPS * time_scale)

    screen.fill((255, 255, 255))

    pygame.draw.circle(
        screen, 0XFF0000,
        (mouse_x, mouse_y),
        2
    )

    On_Target_text = font.render(f'{time_scale}X', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 10))

    robot.display(pygame, screen, body_color=0x00FF00, target_color=0x000FF)
    robot2.display(pygame, screen, body_color=0xFFFF00, target_color=0x0FFFF)

    # # lock position
    # robot.position[0] = 500
    # robot.position[1] = 500

    time.sleep(1 / FPS)
    pygame.display.flip()