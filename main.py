import time

import pygame
from BeeLineRobot import BeeLineRobot
from BasicPathfindBot import BasicPathfindBot
from Field import Field, Circle
from Utils.Position import Position
from Utils.RayCast import ray_cast
from Utils.DebugPrint import DebugPrint
from Utils.DebugPrint import DebugPrint

def time_function(func, *args, **kwargs):
    start_time = time.time()
    func(*args, **kwargs)
    return time.time() - start_time


if __name__ == "__main__":
    DebugPrinter = DebugPrint(1)
    # set up pygame
    pygame.init()
    map_scale = 2
    screen = pygame.display.set_mode((802 * map_scale, 366 * map_scale))  # (field.width, field.height))
    pygame.display.set_caption(f"Collision Test with Field")
    font = pygame.font.Font('freesansbold.ttf', 32)

    # set up clock
    clock = pygame.time.Clock()
    last_time = time.time()

    # set up field, cursor, and robot
    margin = 25
    field = Field(pygame.transform.scale(pygame.image.load("images/Map.png"), (802 * map_scale, 366 * map_scale)), margin=margin)
    cursor = Circle(5, 5, 3)
    robot = BasicPathfindBot(field, max_velocity=400, max_acceleration=600)
    robot.position = Position(screen.get_width()/2, screen.get_height()/2)
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_just_pressed = (False, False, False)

    # track collisions
    collisions = 0
    colliding = False
    robot_running = False

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
                if event.key == pygame.K_c: # clear waypoints if c is pressed
                    robot.trajectory = []
                if event.key == pygame.K_s: # start robot if s is pressed
                    robot_running = True

        # update basics
        time_delta_seconds = time.time() - last_time
        last_time = time.time()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # sets a new waypoint if the left mouse button is pressed
        if pygame.mouse.get_pressed()[0] and not mouse_just_pressed[0]:
            robot.add_waypoint(Position(mouse_x, mouse_y))

        # follow trajectory if there is one
        if robot_running:
            # reset robot if it reaches the end of the trajectory
            if robot.follow_trajectory(time_delta_seconds):
                robot_running = False

        # set margin mask if the middle mouse button is pressed
        # NOTE: this operation is so slow that it may cause the physics to act weirdly, because the time_delta is so big
        if pygame.mouse.get_pressed()[1] and field.margin == margin:
            field.set_margin_mask(abs(margin - 25))  # quirky way to toggle between 0 and 15
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
                screen.blit(font.render(f"Collisions: {collisions}", True, (255, 0, 0)), (10, 50))
                screen.blit(font.render(f"COLLIDED", True, (255, 0, 0)), (screen.get_width()/2, screen.get_height()/2))
                pygame.display.flip()
                time.sleep(0.5)
            
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
        for waypoint_i, waypoint in enumerate(robot.trajectory):
            if waypoint_i == 0:
                pygame.draw.circle(screen, (0, 255, 0), (waypoint.x, waypoint.y), 5)
                pygame.draw.line(screen, (0, 255, 0), (robot.position.x, robot.position.y), (waypoint.x, waypoint.y), 5)
            else:
                pygame.draw.circle(screen, (0, 0, 255), (waypoint.x, waypoint.y), 5)
                pygame.draw.line(screen, (0, 0, 255), (robot.trajectory[waypoint_i-1].x, robot.trajectory[waypoint_i-1].y), (waypoint.x, waypoint.y), 5)

        robot.display(screen)
        # ray cast to cursor
        if len(robot.trajectory):
            if ray_cast(robot.trajectory[-1], Position(mouse_x, mouse_y), field.mask):
                pygame.draw.line(screen, (255, 0, 0), (robot.trajectory[-1].x, robot.trajectory[-1].y), (mouse_x, mouse_y), 5)
            else:
                pygame.draw.line(screen, (0, 255, 0), (robot.trajectory[-1].x, robot.trajectory[-1].y), (mouse_x, mouse_y), 5)
        else:
            if ray_cast(robot.position, Position(mouse_x, mouse_y), field.mask):
                pygame.draw.line(screen, (255, 0, 0), (robot.position.x, robot.position.y), (mouse_x, mouse_y), 5)
            else:
                pygame.draw.line(screen, (0, 255, 0), (robot.position.x, robot.position.y), (mouse_x, mouse_y), 5)

        # draw everything
        screen.blit(font.render(f"Collisions: {collisions}", True, (255, 0, 0)), (10, 50))
        cursor.draw(screen)
        screen.blit(font.render(f"Framerate: {round(1 / (time_delta_seconds + 0.00001), 2)}", True, (255, 0, 0)),
                    (10, 90))
        screen.blit(font.render("Current Speed: ", True, (255, 0, 0)),
                    (10, 130))
        circle_color = (125, 125, 125)
        # to show velocity
        pygame.draw.circle(screen, circle_color, (280, 145), 15)

        pygame.draw.line(screen, (0, 0, 255), (280, 145),
                         (280 + robot.velocity.x, 145 + robot.velocity.y), 5)
        pygame.display.update()

        # tick clock
        clock.tick(50)  # change this to change the framerate. -1 means unlimited
        # update just pressed
        mouse_just_pressed = pygame.mouse.get_pressed()

        DebugPrinter.update()
