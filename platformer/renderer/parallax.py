import pygame
from typing import List

from core import constants, resources

from . import base


PARALLAX_SPEED: float = 7.5


class ParallaxRenderer:
    def __init__(self, camera: base.Camera, target: pygame.Surface, cache: resources.Cache):
        self.camera = camera
        self.target = target
        self.cache = cache

        # load first background
        self.background = None
        self.load_background(0)

    def load_background(self, index: int) -> None:
        """Loads the nth set of background images."""
        background_files = self.cache.paths.all_backgrounds()
        background_path = self.cache.paths.background(background_files[index])
        self.background = self.cache.get_image(background_path)

        # upscale as necessary
        for i in range(constants.NUM_SCALE_DOUBLE):
            self.background = pygame.transform.scale2x(self.background)

    def get_num_layers(self) -> int:
        """Returns how many layers with a height of RESOLUTION_Y fit inside the loaded background."""
        return self.background.get_height() // constants.RESOLUTION_Y

    def get_layer_rect(self, index: int) -> pygame.Rect:
        """Creates a clipping rect for the nth background layer.

        Each layer is 100% width and has height equal to RESOLUTION_Y. The number of layers is detected automatically.
        """
        width = self.background.get_width()
        return pygame.Rect(0, index * constants.RESOLUTION_Y, width, constants.RESOLUTION_Y)

    @staticmethod
    def get_layer_speed(index: int) -> float:
        return index + 0.5

    def draw_layer(self, x: int, clip: pygame.Rect) -> None:
        """Draws the background from the clipping rectangle at given position."""
        width = self.background.get_width()
        self.target.blit(self.background, (-x % width - width, 0), clip)
        self.target.blit(self.background, (-x % width, 0), clip)

    def draw(self) -> None:
        for index in range(self.get_num_layers()):
            x = int(self.camera.topleft.x * self.get_layer_speed(index) * PARALLAX_SPEED)
            clip = self.get_layer_rect(index)
            self.draw_layer(x, clip)

    def update(self, elapsed_ms: int) -> None:
        pass
