import pygame

from abc import ABC, abstractmethod


class Camera:
    def __init__(self, width: int, height: int):
        self.center = pygame.math.Vector2()
        self.width = width
        self.height = height

    def from_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Transforms coordinates form world to cam
        Example: Camera (topleft) at (2|3) moves all coordinates using (-2|-3).
        """
        x = pos.x - self.center.x
        y = pos.y - self.center.y
        return pygame.math.Vector2(x, y)

    def to_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Transforms coordinates from cam/screen to world."""
        x = pos.x + self.center.x
        y = pos.y + self.center.y
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
