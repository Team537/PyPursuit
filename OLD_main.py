import math
import os
import random
import time

import pygame

from OLD_Robot import OLD_Robot
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

scale = 3

robots = [
    OLD_Robot(
    Position(screen.get_size()[0] / 2, screen.get_size()[1] / 2),
    max_accelerations=Position(100 * scale, 100 * scale, 150 * scale),
    # max_accelerations=Position(100 * random.random() * scale, 100 * random.random() * scale, 60 + 50 * random.random()),
    max_velocity=300 * scale) for i in range(5**2)
]

running = True

FPS = 240

time_scale = 1

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    time_passed = (time.time_ns() / 1e9 - last_time) * time_scale
    last_time = time.time_ns() / 1e9

    mouse_x, mouse_y = pygame.mouse.get_pos()
    screen.fill((255, 255, 255))

    pygame.draw.circle(
        screen, 0XFF0000,
        (mouse_x, mouse_y),
        2
    )

    text = font.render(f'{time_scale}X', True, [0, 0, 255])
    screen.blit(text, (10, 10))

    robots_at_target = 0

    for index, robot in enumerate(robots):
        length = math.ceil(math.sqrt(len(robots)))
        x_offset = (index % length - length / 2) * 15 + 7.5
        y_offset = (index // length - length / 2) * 15 + 7.5

        if pygame.mouse.get_pressed()[0]:
            x_offset += random.randrange(-1000, 1000)
            y_offset += random.randrange(-1000, 1000)
        elif pygame.mouse.get_pressed()[2]:
            x_offset *= 80
            y_offset *= 80

        robot.go_to_position(Position(mouse_x + x_offset, mouse_y + y_offset), time_difference=time_passed)
        robot.display(pygame, screen)

        pygame.draw.circle(
            screen, 0XFF0000,
            (mouse_x + x_offset, mouse_y + y_offset),
            2
        )
        robots_at_target += robot.position.get_distance_to(Position(mouse_x + x_offset, mouse_y + y_offset)) < 1

    if robots_at_target == len(robots):
        color = [0, 255, 0]
    else:
        color = [255, 0, 0]
    text = font.render(f'{robots_at_target} on target', True, color)
    screen.blit(text, (10, 60))

    text = font.render(f'{1/time_passed * time_scale} FPS', True, color)
    screen.blit(text, (10, 90))

    # # lock position
    # robot.position[0] = 500
    # robot.position[1] = 500

    time.sleep(1 / FPS)
    pygame.display.flip()