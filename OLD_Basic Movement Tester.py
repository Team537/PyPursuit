import math
import time
import os

import pygame

from AccelerationSmoother import AccelerationSmoother, sign

from Rotation import Rotation

pygame.init()


def every_delay(delay):
    global last_time
    if time.time_ns() / 1e9 - last_time >= delay:
        last_time = time.time_ns() / 1e9
        return True
    return False

screen = pygame.display.set_mode((1000, 1000))

font = pygame.font.Font('freesansbold.ttf', 32)

pygame.display.set_caption(f"Slew Rate Limter Test")

running = True

magnitude_smoother = AccelerationSmoother(0.2)
rotation_smoother = AccelerationSmoother(720)  # In degrees

PPS = 100

last_time = time.time_ns() / 1e9

FPS = 165

time.sleep(1 / FPS)

FPS_text = font.render(f'FPS: {FPS}', True, [0, 0, 255])

follower_x = 500
follower_y = 500
follower_direction = 0
follower_rotation = Rotation(0)

while running:
    # follower_x = 500
    # follower_y = 500
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    screen.blit(FPS_text, (10, 10))

    x, y = pygame.mouse.get_pos()

    # magnitude should be positive if it's on the right, and negetive if it's on the left
    target_magnitude = math.sqrt((x - follower_x) ** 2 + (y - follower_y) ** 2) / PPS
    #rotaiton should never be negative
    target_rotation = Rotation(math.atan2(y - follower_y, -(x - follower_x)) * 180 / math.pi + 180)

    On_Target_text = font.render(f'{target_magnitude=}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 120))

    On_Target_text = font.render(f'{target_rotation=}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 180))

    if every_delay(0.25):
        os.system('cls')
        print(f"{target_magnitude=}\n{target_rotation=}")
        magnitude = magnitude_smoother.update(current_target=target_magnitude/PPS, print_debug=True) * PPS
        rotation = rotation_smoother.update(current_target=target_rotation, print_debug=True)
        # print
        # magnitude * math.cos(rotation * math.pi / 180)
        # magnitude * math.sin(rotation * math.pi / 180)
        print(f"x = {magnitude * math.cos(rotation * math.pi / 180)}\n" +
              f"y = {magnitude * math.sin(rotation * math.pi / 180)}")

    else:
        magnitude = magnitude_smoother.update(current_target=target_magnitude/PPS) * PPS
        rotation = rotation_smoother.update(current_target=target_rotation)

    On_Target_text = font.render(f'{magnitude=}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 270))

    On_Target_text = font.render(f'{rotation=}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 360))

    On_Target_text = font.render(f'At Target?: {magnitude_smoother._current_direction}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 60))

    On_Target_text = font.render(f'Acceleration?: {magnitude_smoother._current_acceleration}', True, [0, 0, 255])
    screen.blit(On_Target_text, (10, 420))
    # draw circle at position of follower using magnitude and rotation
    # equation to convert magnitutde and rotation to x and y
    # x = magnitude * cos(rotation)
    # y = magnitude * sin(rotation)

    follower_x += magnitude * math.cos(rotation * math.pi / 180)
    follower_y -= magnitude * math.sin(rotation * math.pi / 180)

    pygame.draw.circle(
        screen, 0x00FF00,
        (follower_x, follower_y),
        20
    )

    pygame.draw.line(screen, 0x0000FF, (follower_x, follower_y), (follower_x + magnitude * math.cos(rotation * math.pi / 180) * PPS, follower_y - magnitude * math.sin(rotation * math.pi / 180) * PPS))

    pygame.draw.circle(
        screen, 0xFF0000,
        (x, y),
        5
    )
    time.sleep(1 / FPS)
    pygame.display.flip()
