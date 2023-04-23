import pygame
import math

from core import constants, resources

from . import base


PARALLAX_SPEED: float = 7.5

CLOUD_LAYER: int = 0
CLOUD_SPEED: float = 0.5
CLOUD_DELTA_Y: float = CLOUD_SPEED * 5
CLOUD_PERIOD_LENGTH: float = 15.0


class ParallaxRenderer:
    def __init__(self, camera: base.Camera, target: pygame.Surface, cache: resources.Cache):
        self.camera = camera
        self.target = target
        self.cache = cache

        # load first background
        self.background = None
        self.load_background(0)

        self.clouds_offset = 0
        self.cloud_speed = 1.0

    def load_background(self, index: int) -> None:
        """Loads the nth set of background images."""
        background_files = self.cache.paths.all_backgrounds()
        background_path = self.cache.paths.background(background_files[index])
        self.background = pygame.transform.scale_by(self.cache.get_image(background_path), 2)

    def get_fill_color(self) -> pygame.Color:
        """Grab first pixels color."""
        return self.background.get_at((0, 0))

    def get_num_layers(self) -> int:
        """Returns how many layers with a height of RESOLUTION_Y fit inside the loaded background."""
        return self.background.get_height() // constants.RESOLUTION_Y

    def get_layer_rect(self, index: int) -> pygame.Rect:
        """Creates a clipping rect for the nth background layer.

        Each layer is 100% width and has height equal to RESOLUTION_Y. The number of layers is detected automatically.
        """
        width = self.background.get_width()
        return pygame.Rect(0, index * constants.RESOLUTION_Y, width, constants.RESOLUTION_Y)

    def get_layer_speed(self, index: int) -> float:
        return (index + 1) / self.get_num_layers() * 2

    def draw_layer(self, x: int, y: int, clip: pygame.Rect) -> None:
        """Draws the background from the clipping rectangle at given position."""
        width = self.background.get_width()
        num_repeats = pygame.display.get_window_size()[0] / width

        self.target.blit(self.background, (-x % width - width, y), clip)
        for i in range(int(num_repeats+1)):
            self.target.blit(self.background, (-x % width + i * width, y), clip)

    def draw(self) -> None:
        y0 = pygame.display.get_window_size()[1] - constants.RESOLUTION_Y

        for index in range(self.get_num_layers()):
            x = int(self.camera.topleft.x * self.get_layer_speed(index) * PARALLAX_SPEED)
            y = y0
            if index == CLOUD_LAYER:
                x += self.clouds_offset * CLOUD_SPEED * self.cloud_speed
                y -= math.cos(self.clouds_offset / CLOUD_PERIOD_LENGTH) * CLOUD_DELTA_Y * self.cloud_speed
            clip = self.get_layer_rect(index)
            self.draw_layer(x, y, clip)

    def update(self, elapsed_ms: int) -> None:
        self.clouds_offset += elapsed_ms * 0.025
