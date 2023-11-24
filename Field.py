import pygame
from pygame import sprite


class Field(sprite.Sprite):
    def __init__(self, image: pygame.image):
        super().__init__()
        self.width = image.get_width()
        self.height = image.get_height()

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((255, 255, 255, 0))
        self.image.blit(image, (0, 0))

        # make image transparent
        self.image = self.image.convert_alpha()
        # make white pixels transparent
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                if self.image.get_at((x, y)) == (255, 255, 255, 255):
                    self.image.set_at((x, y), (255, 255, 255, 0))
        # sets stuff up for collision detection
        self.rect = self.image.get_rect()
        self.rect.center = (self.width / 2, self.height / 2)
        self.mask = pygame.mask.from_surface(self.image)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Circle(sprite.Sprite):
    def __init__(self, x: float, y: float, radius: float):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius
        self.surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (0, 255, 0, 255), (radius, radius), radius)
        self.rect = self.surface.get_rect()
        self.rect.center = (x, y)
        self.mask = pygame.mask.from_surface(self.surface)

    def set_color(self, color: tuple[int, int, int, int]) -> None:
        """Sets the color of the circle
        :param color: the color to set to (r, g, b, a)
        :return: None"""
        pygame.draw.circle(self.surface, color, (self.radius, self.radius), self.radius)

    def draw(self, screen: pygame.Surface) -> None:
        """Draws the circle to the given surface
        :param screen: the surface to draw to
        :return: None"""
        screen.blit(self.surface, (self.x - self.radius, self.y - self.radius))

    def move_to(self, x: float, y: float, check: bool | pygame.mask.Mask = False) -> None:
        """Moves the circle to the given position. If check is a mask, it will check for collisions with the given
        mask
        :param x: the x position to move to
        :param y: the y position to move to
        :param check: the mask to check for collisions with, or False to not check for collisions with any
        :return: None"""

        if check:
            if not self.can_move_to_position(check, x, y):
                return

        self.x = x
        self.y = y
        self.rect.center = (x, y)

    def can_move_to_position(self, other: pygame.mask.Mask, x: int | float, y: int | float) -> bool:
        """Checks if the circle can move to the given position without colliding with the given mask
        :param other: the mask to check for collisions with
        :param x: the x position to check
        :param y: the y position to check
        :return: True if the circle can move to the given position without colliding with the given mask, False"""
        return self.mask.overlap(other, (-x + self.radius, -y + self.radius)) is None
