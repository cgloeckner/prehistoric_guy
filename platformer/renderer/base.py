import pygame

from abc import ABC, abstractmethod


# noinspection SpellCheckingInspection
class Camera:
    def __init__(self, width: int, height: int):
        # noinspection SpellCheckingInspection
        self.topleft = pygame.math.Vector2()
        self.width = width
        self.height = height

    def set_center(self, pos: pygame.math.Vector2, scale: int) -> None:
        """Sets the camera center (world scale) to the given point."""
        tmp = pos.copy()
        tmp.x -= (self.width // scale) // 2
        tmp.y -= (self.height // scale) // 2
        self.topleft = tmp

    def rect_is_visible(self, rect: pygame.Rect) -> bool:
        """Returns whether the given rect is within the visible area. This assumes its position is already relative to
        the camera."""
        return (0 <= rect.left < self.width or 0 <= rect.right < self.width) and \
            (0 <= rect.top < self.height or 0 <= rect.bottom < self.height)

    def from_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        # noinspection SpellCheckingInspection
        """Transforms coordinates form world to cam
                Example: Camera (top left) at (2|3) moves all coordinates using (-2|-3).
                """
        x = pos.x - self.topleft.x
        y = pos.y - self.topleft.y
        return pygame.math.Vector2(x, y)

    def to_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Transforms coordinates from cam/screen to world."""
        x = pos.x + self.topleft.x
        y = pos.y + self.topleft.y
        return pygame.math.Vector2(x, y)


class Renderer(ABC):
    def __init__(self, camera: Camera):
        self.camera = camera

    @abstractmethod
    def update(self, elapsed_ms: int) -> None:
        ...

    @abstractmethod
    def draw(self) -> None:
        ...
