import pygame
from pygame import sprite


class Field(sprite.Sprite):
    def __init__(self, image: pygame.image, margin: int = 0):
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
        self.margin_mask = None
        self.set_margin_mask(margin)

    def draw(self, screen, show_margin_mask=False, _margin_mask_surface=[None]):
        """Draws the field to the given surface
        :param screen: the surface to draw to
        :param show_margin_mask: if the margin mask should be drawn
        :param _margin_mask_surface: don't use this, it's for internal use only
        :return: None"""
        if _margin_mask_surface == [None]:
            original = self.image.copy()
            margins = self.margin_mask.to_surface(setcolor=(125, 125, 125), unsetcolor=(255, 255, 255))
            margins.blit(original, (0, 0))
            _margin_mask_surface[0] = margins
        if show_margin_mask:
            screen.blit(_margin_mask_surface[0], self.rect)
        else:
            screen.blit(self.image, self.rect)

    def set_margin_mask(self, margin: int) -> pygame.mask.Mask:
        """Sets the margin mask to the given margin.
        Note that this is an incredibly slow operation, so it should only be done once
        :param margin: the margin to set to
        :return: None"""
        if margin == 0:
            self.margin_mask = self.mask
            return self.margin_mask

        margin_mask = pygame.mask.from_surface(self.image, margin).to_surface(unsetcolor=(255, 255, 255, 0))
        points = []
        for x in range(margin_mask.get_size()[0]):
            for y in range(margin_mask.get_size()[1]):
                if margin_mask.get_at((x, y)) == (255, 255, 255, 255):
                    points.append((x, y))

        for x, y in points:
            pygame.draw.circle(margin_mask, (255, 255, 255, 255), (x, y), margin)

        self.margin_mask = pygame.mask.from_surface(margin_mask)
        return self.margin_mask

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
