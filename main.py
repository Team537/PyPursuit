import time

import pygame
from BeeLineRobot import BeeLineRobot
from Field import Field, Circle
from Position import Position

if __name__ == "__main__":
    # set up pygame
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))  # (field.width, field.height))
    pygame.display.set_caption(f"Collision Test with Field")
    font = pygame.font.Font('freesansbold.ttf', 32)

    # set up clock
    clock = pygame.time.Clock()
    last_time = time.time()

    # set up field, cursor, and robot
    field = Field(pygame.image.load("images/TestField.png"))
    cursor = Circle(5, 5, 10)
    robot = BeeLineRobot(max_accelerations=Position(500, 500, 10), max_velocity=250)
    robot.position = Position(500, 500)
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # track collisions
    collisions = 0
    colliding = False

    # main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # quit when the window is closed

            # check for key presses
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # reset collision count if r is pressed
                    collisions = 0

        # update time
        time_delta = time.time() - last_time
        last_time = time.time()
        time_delta_seconds = time_delta / 1000

        # update background
        screen.fill((255, 255, 255))
        field.draw(screen)

        # update mouse position
        if not pygame.mouse.get_pressed()[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            cursor.move_to(mouse_x, mouse_y)

        # check for collisions with cursor
        if pygame.sprite.collide_mask(cursor, field):
            screen.blit(font.render(f"Collision", True, (255, 0, 0)), (10, 10))
            cursor.set_color((255, 0, 0, 255))
        else:
            screen.blit(font.render(f"Collision", True, (255, 0, 0)), (10, 10))
            cursor.set_color((0, 255, 0, 255))

        # update robot position
        robot.go_to_position(Position(mouse_x, mouse_y), time_delta_seconds=time_delta, debug=False)
        robot.display(screen)

        # check for collisions with robot
        if robot.collided_with_field(field):
            if not colliding:  # updates collision
                collisions += 1
                colliding = True  # this makes sure we don't call it multiple times in the same collision
            robot.sprite.set_color((255, 0, 0, 255))
        else:
            colliding = False
            robot.sprite.set_color((0, 255, 0, 255))

        # draw everything
        screen.blit(font.render(f"Collisions: {collisions}", True, (255, 0, 0)), (10, 50))
        screen.blit(font.render(f"Framerate: {round(clock.get_fps(), 2)}", True, (255, 0, 0)), (10, 90))
        cursor.draw(screen)
        pygame.display.update()