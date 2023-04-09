import pygame
import os
from typing import Dict, Tuple

from constants import *
import animations


def fill_pixels(surface: pygame.Surface, color: pygame.Color):
    """Replaces all non-transparent pixels with the given color.
    """
    pixels = pygame.PixelArray(surface)

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 != 0:
                pixels[x, y] = color

    pixels.close()


COLOR_TUPLE = Tuple[int, int, int]
RECT_TUPLE = Tuple[int, int, int, int]


class Cache(object):
    """Caches resources and eventually loads the image from a root directory.
    All images are supposed to be in PNG format with the file extension .png"""

    def __init__(self, root='./data'):
        """Initializes the cache with the given root directory.
        """
        self.root = root

        # regular resources
        self.images: Dict[str, pygame.Surface] = dict()
        self.fonts: Dict[str, pygame.font.Font] = dict()

        # sprites include their flipped frames
        self.sprites: Dict[str, pygame.Surface] = dict()

        # colored and rotated surfaces
        self.colored: Dict[Tuple[pygame.Surface, COLOR_TUPLE]] = dict()
        self.rotated: Dict[Tuple[pygame.Surface, RECT_TUPLE, bool]] = dict()

    def get_image(self, filename: str) -> pygame.Surface:
        """Loads the image via filename. If already loaded, it's taken from the cache.
        Returns the image's surface.
        """
        if filename not in self.images:
            path = os.path.join(self.root, f'{filename}.png')
            self.images[filename] = pygame.image.load(path)

        return self.images[filename]

    def get_sprite_sheet(self, filename: str) -> pygame.Surface:
        """Adds the x-flipped sprites into the sprite sheet.
        Returns the finished sheet
        """
        if filename not in self.sprites:
            image = self.get_image(filename)
            self.sprites[filename] = animations.flip_sprite_sheet(image, SPRITE_SCALE)

        return self.sprites[filename]

    def get_font(self, fontname: str = '', font_size: int = 18) -> pygame.font.Font:
        """Loads a SysFont via filename and size.
        Returns the font object.
        """
        if fontname == '':
            return pygame.font.SysFont(pygame.font.get_default_font(), font_size)

        # FIXME: implement font loading
        raise NotImplementedError()

    def get_colored_surface(self, surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
        """If not cached, a copy of the given surface is created and all non-transparent pixels are replaced with the
        given color. If cached, the existing copy is used.
        Returns the colored surface.
        """
        key = (surface, (color.r, color.g, color.b))
        if key not in self.colored:
            self.colored[key] = surface.copy()
            fill_pixels(self.colored[key], color)

        return self.colored[key]

    def get_rotated_surface_clip(self, surface: pygame.Surface, rect: pygame.Rect, angle: float, flip: bool)\
            -> pygame.Surface:
        """If not cached, a part of the surface, described by the given rect, is created and rotated. This copy is
        cached for each integer angle in [0; 360). Flipping the frame x-wise is also supported.
        Returns the rotated surface.
        """
        key = (surface, tuple(rect), flip)
        if key not in self.rotated:
            # grab and rotate frame
            frame = surface.subsurface(rect)
            if flip:
                frame = pygame.transform.flip(frame, flip_x=True, flip_y=False)
                self.rotated[key] = [pygame.transform.rotate(frame, alpha) for alpha in range(360)]
            else:
                self.rotated[key] = [pygame.transform.rotate(frame, -alpha) for alpha in range(360)]

        return self.rotated[key][int(angle) % 360]
