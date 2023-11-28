import time

import pygame
from BeeLineRobot import BeeLineRobot
from Field import Field, Circle
from Position import Position
from RayCast import ray_cast
from random import randint


def normal():
    # pauses the robot if the left mouse button is pressed
    if not pygame.mouse.get_pressed()[0]:
        robot.go_to_position(robot.path_find(Position(mouse_x, mouse_y)), time_delta_seconds=time_delta_seconds,
                             debug=False)

    # check for collisions with cursor
    if pygame.sprite.collide_mask(cursor, field):
        cursor.set_color((255, 0, 0, 255))
    else:
        cursor.set_color((0, 255, 0, 255))

    # check for collisions with robot
    if robot.collided_with_mask(field.mask, ignore_if=field.green_mask):
        return 1  # failed

    elif robot.collided_with_mask(field.green_mask):
        return 2  # success

    """Draw everything"""
    # update background
    screen.fill((255, 255, 255))
    field.draw(screen, show_margin_mask=True)

    # update robot display
    robot.display(screen)

    # ray cast to cursor
    if ray_cast(robot.position, Position(mouse_x, mouse_y), field.mask):
        pygame.draw.line(screen, (255, 0, 0), (robot.position.x, robot.position.y), (mouse_x, mouse_y), 5)
    else:
        pygame.draw.line(screen, (0, 255, 0), (robot.position.x, robot.position.y), (mouse_x, mouse_y), 5)

        screen.blit(font.render(f"Framerate: {round(1 / (time_delta_seconds + 0.00001), 2)}", True, (255, 0, 0)),
                    (10, 90))
        screen.blit(font.render(f"Time: {round(time.time() - start_time, 3)}", True, (255, 0, 0)),
        (10, 30))

    # draw everything
    cursor.draw(screen)
    return 0  # normal

def win_screen():
    global final_time
    if final_time == [None]:
        final_time[0] = round(time.time() - start_time, 3)
    screen.fill((255, 255, 255))
    screen.blit(font.render(f"Success!", True, (255, 0, 0)), (400, 400))
    screen.blit(font.render(f"Your final time was: {final_time[0]} seconds", True, (255, 0, 0)), (200, 460))

def loose_screen_jump():
    global run
    a = 10
    if run == [None]:
        time.sleep(5)
        boo = pygame.image.load("images/boo.png")
        boo = pygame.transform.scale(boo, (screen.get_size()[0] + a * 2, screen.get_size()[1] + a * 2))
        run[0] = boo
<<<<<<< Updated upstream
        pygame.mixer.Sound.play(pygame.mixer.Sound("images/boo.mp3"))
=======
<<<<<<< HEAD
        fun = pygame.mixer.Sound("images/boo.mp3")
        fun.set_volume(0.6) # spare the ear drums
        pygame.mixer.Sound.play(fun)
=======
        pygame.mixer.Sound.play(pygame.mixer.Sound("images/boo.mp3"))
>>>>>>> bc2964f444c16525d9c04e4d78378fb22f042781
>>>>>>> Stashed changes
    screen.blit(run[0], (randint(-a, a), randint(-a, a)))

def loose_screen():
    screen.fill((0, 0, 0))
    screen.blit(font.render(f"Failed... :(", True, (255, 0, 0)), (400, 400))


if __name__ == "__main__":
    # set up pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))  # (field.width, field.height))
    pygame.display.set_caption(f"Maze Fun")
    font = pygame.font.Font('freesansbold.ttf', 32)

    # set up clock
    clock = pygame.time.Clock()
    last_time = time.time()
    start_time = time.time()

    # set up field, cursor, and robot
    margin = 0
    field = Field(pygame.image.load("images/Maze.png"), margin=margin)
    cursor = Circle(1, 1, 3)
    robot = BeeLineRobot(max_velocity=750)
    robot.position = Position(1, 1)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    final_time = [None]
    run = [None]

    state = 0
    ben = 5.231

    # main loop
    running = True
    bob = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # quit when the window is closed

            # check for key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r or event.key == pygame.K_t:  # reset collision count if r is pressed
<<<<<<< Updated upstream
                    if not (bob and time.time() - bob < ben + 3):
=======
<<<<<<< HEAD
                    if not (bob and time.time() - bob < ben + 8):
=======
                    if not (bob and time.time() - bob < ben + 3):
>>>>>>> bc2964f444c16525d9c04e4d78378fb22f042781
>>>>>>> Stashed changes
                        state = 0
                        robot.position = Position(1, 1)
                        final_time = [None]
                        run = [None]
                        start_time = time.time()
                    if event.key == pygame.K_t:
                        bob = time.time()
<<<<<<< Updated upstream
                    elif time.time() - bob > ben + 3:
=======
<<<<<<< HEAD
                    elif time.time() - bob > ben + 8:
=======
                    elif time.time() - bob > ben + 3:
>>>>>>> bc2964f444c16525d9c04e4d78378fb22f042781
>>>>>>> Stashed changes
                        bob = False

        # update time
        time_delta_seconds = time.time() - last_time
        last_time = time.time()

        # pause the cursor if the right mouse button is pressed
        mouse_x, mouse_y = pygame.mouse.get_pos()
        cursor.move_to(mouse_x, mouse_y)

        if bob != False and time.time() - bob > ben:
            loose_screen_jump()
        elif state == 0:
            state = normal()
        elif state == 1:
            loose_screen()
        elif state == 2:
            win_screen()

        pygame.display.update()
        # tick clock
        clock.tick(-1)  # change this to change the framerate. -1 means unlimited