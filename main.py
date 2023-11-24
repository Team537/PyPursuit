import time

import pygame
from BeeLineRobot import BeeLineRobot
from Field import Field, Circle
from Position import Position
from RayCast import ray_cast


def time_function(func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    return time.time() - start_time


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
    margin = 15
    field = Field(pygame.image.load("images/TestField.png"), margin=margin)
    cursor = Circle(5, 5, 3)
    robot = BeeLineRobot(max_velocity=750)
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
        time_delta_seconds = time.time() - last_time
        last_time = time.time()

        # pause the cursor if the right mouse button is pressed
        if not pygame.mouse.get_pressed()[2]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            cursor.move_to(mouse_x, mouse_y)

        # pauses the robot if the left mouse button is pressed
        if not pygame.mouse.get_pressed()[0]:
            robot.go_to_position(robot.path_find(Position(mouse_x, mouse_y)), time_delta_seconds=time_delta_seconds,
                                 debug=False)

        # set margin mask if the middle mouse button is pressed
        # NOTE: this operation is so slow that it may cause the physics to act weirdly, because the time_delta is so big
        if pygame.mouse.get_pressed()[1] and field.margin == margin:
            field.set_margin_mask(abs(margin - 15))  # weird way to toggle between 0 and 15
        elif not pygame.mouse.get_pressed()[1] and field.margin != margin:  # super hacky way to run once per click
            margin = field.margin

        # check for collisions with cursor
        if pygame.sprite.collide_mask(cursor, field):
            cursor.set_color((255, 0, 0, 255))
        else:
            cursor.set_color((0, 255, 0, 255))

        # check for collisions with robot
        if robot.collided_with_mask(field.mask):
            if not colliding:  # updates collision
                collisions += 1
                colliding = True  # this makes sure we don't call it multiple times in the same collision
            robot.sprite.set_color((255, 0, 0, 255))
        elif robot.collided_with_mask(field.margin_mask):  # check if robot is in the margin
            robot.sprite.set_color((255, 125, 0, 255))
        else:
            colliding = False
            robot.sprite.set_color((0, 255, 0, 255))

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

        # draw everything
        screen.blit(font.render(f"Collisions: {collisions}", True, (255, 0, 0)), (10, 50))
        cursor.draw(screen)
        screen.blit(font.render(f"Framerate: {round(1 / (time_delta_seconds + 0.00001), 2)}", True, (255, 0, 0)),
                    (10, 90))
        pygame.display.update()

        # tick clock
        clock.tick(-1)  # change this to change the framerate
