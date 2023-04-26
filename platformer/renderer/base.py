import pygame
from typing import Optional, Tuple
from abc import ABC, abstractmethod

from core import constants


class Camera:
    def __init__(self, size: Optional[Tuple[int, int]] = None, scale: Optional[int] = None):
        self.topleft = pygame.math.Vector2()
        self.width, self.height = pygame.display.get_window_size() if size is None else size
        if constants.SCALE_2X:
            self.width //= 2
            self.height //= 2
        self.scale = constants.WORLD_SCALE if scale is None else scale

    def reset_pos(self) -> None:
        """Reset camera position to (0, 0)."""
        self.topleft = pygame.math.Vector2()

    def set_center_x(self, x: float) -> None:
        """Sets the camera center x (world scale) to the given coordinate."""
        self.topleft.x = x - (self.width // self.scale) // 2

    def set_center_y(self, y: float) -> None:
        """Sets the camera center y (world scale) to the given coordinate."""
        self.topleft.y = y - (self.height // self.scale) // 2

    def set_center(self, x: float, y: float) -> None:
        """Sets the camera center (world scale) to the given point."""
        self.set_center_x(x)
        self.set_center_y(y)

    def rect_is_visible(self, rect: pygame.Rect) -> bool:
        """Returns whether the given rect is within the visible area. This assumes its position is already relative to
        the camera."""
        return (-constants.WORLD_SCALE <= rect.left < self.width or 0 <= rect.right < self.width) and \
            (-constants.WORLD_SCALE <= rect.top < self.height or 0 <= rect.bottom < self.height)

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
        x, y = pos.xy
        x = x + self.topleft.x
        y = y + self.topleft.y
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
