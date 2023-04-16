import pygame

from abc import ABC, abstractmethod


class Camera(pygame.Rect):
    def __init__(self, width: int, height: int):
        super().__init__(0, 0, width, height)

    def world2cam_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Transforms coordinates form world to cam
        Example: Camera (topleft) at (2|3) moves all coordinates using (-2|-3).
        """
        x = pos.x - self.left
        y = pos.y - self.top
        return pygame.math.Vector2(x, y)

    def cam2world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Transforms coordinates from cam/screen to world.
        """
        x = pos.x + self.left
        y = pos.y + self.top
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
