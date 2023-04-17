import pygame
import pathlib
from dataclasses import dataclass
from typing import Dict, Tuple, List, Optional

from core.constants import *


@dataclass
class HslTransform:
    """
    hue: [0; 360)
    saturation: [0; 100]
    lightness: [0; 100]
    """
    hue: Optional[float] = None
    saturation: Optional[float] = None
    lightness: Optional[float] = None


def transform_image_hsl(surface: pygame.Surface, transform: HslTransform, color_strings: List[str] = None) -> None:
    """Rotates a surface's colors in place. Only pixels are modified whose color is in the given list. The alteration
    is based on the given delta tuple: hue, saturation, lightness. Transparent pixels are ignored.
    """
    pixels = pygame.PixelArray(surface)
    matching = [pygame.Color(c) for c in color_strings] if color_strings is not None else []

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 == 0:
                continue

            color = surface.unmap_rgb(pixels[x, y])
            if len(matching) > 0 and color not in matching:
                continue

            # change pixel's hue (rotated) and saturation / lightness (bound)
            hue, sat, light, alpha = color.hsla
            if transform.hue is not None:
                hue = transform.hue % 360.0
            if transform.saturation is not None:
                sat = max(0.0, min(100.0, transform.saturation))
            if transform.lightness is not None:
                light = max(0.0, min(100.0, transform.lightness))
            color.hsla = hue, sat, light, alpha
            pixels[x, y] = surface.map_rgb(color)

    pixels.close()


def flip_sprite_sheet(src: pygame.Surface, tile_size: int) -> pygame.Surface:
    """Splits all sprite frames but keeps the logical order of the entire sprite sheet.
    A new sprite sheet is returned which holds all sprites (left: original, right: flipped frames).
    """
    size = src.get_size()
    mirr = pygame.transform.flip(src, flip_x=True, flip_y=False)
    dst = pygame.Surface((size[0] * 2, size[1]), flags=pygame.SRCALPHA)

    dst.blit(src, (0, 0))
    for column in range(src.get_width() // tile_size):
        dst.blit(mirr, (size[0] + column * tile_size, 0), (size[0] - (column + 1) * tile_size, 0, tile_size, size[1]))

    return dst


def fill_pixels(surface: pygame.Surface, color: pygame.Color):
    """Replaces all non-transparent pixels with the given color in place."""
    pixels = pygame.PixelArray(surface)

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 != 0:
                pixels[x, y] = color

    pixels.close()


COLOR_TUPLE = Tuple[int, int, int]
RECT_TUPLE = Tuple[int, int, int, int]
HSL_TUPLE = Tuple[float, float, float]


class Cache(object):
    """Caches resources and eventually loads the image from a root directory.
    All images are supposed to be in PNG format with the file extension .png"""

    def __init__(self, root='./data'):
        """Initializes the cache with the given root directory.
        """
        self.root = pathlib.Path(root)

        # regular resources
        self.images: Dict[str, pygame.Surface] = dict()
        self.fonts: Dict[str, pygame.font.Font] = dict()

        # sprites include their flipped frames
        self.sprites: Dict[str, pygame.Surface] = dict()

        # hsl-transformed and rotated surfaces
        self.hsl_transforms: Dict[Tuple[pygame.Surface, HSL_TUPLE, Optional[COLOR_TUPLE]]] = dict()
        self.rotated: Dict[Tuple[pygame.Surface, RECT_TUPLE, bool], List[pygame.Surface]] = dict()

    def get_image_filename(self, filename: str) -> pathlib.Path:
        """Returns full path object including file extension."""
        return self.root / f'{filename}.png'

    def get_image(self, filename: str) -> pygame.Surface:
        """Loads the image via filename. If already loaded, it's taken from the cache. Returns the image's surface."""
        if filename not in self.images:
            path = self.get_image_filename(filename)
            self.images[filename] = pygame.image.load(path)

        return self.images[filename]

    def get_sprite_sheet(self, filename: str) -> pygame.Surface:
        """Adds the x-flipped sprites into the sprite sheet. Returns the finished sheet."""
        if filename not in self.sprites:
            image = self.get_image(filename)
            self.sprites[filename] = flip_sprite_sheet(image, SPRITE_SCALE)

        return self.sprites[filename]

    def get_font(self, fontname: str = '', font_size: int = 18) -> pygame.font.Font:
        """Loads a SysFont via filename and size. Returns the font object."""
        if fontname == '':
            return pygame.font.SysFont(pygame.font.get_default_font(), font_size)

        # FIXME: implement font loading
        raise NotImplementedError()

    def get_hsl_transformed(self, surface: pygame.Surface, hsl: HslTransform, colors: List[str] = None)\
            -> pygame.Surface:
        """If not cached, a copy of the given surface is created and all non-transparent pixels are replaced with the
        given color. If cached, the existing copy is used.
        Only colors specified are altered.
        Returns the colored surface.
        """
        hsl_tuple = (hsl.hue, hsl.saturation, hsl.lightness)
        color_tuple = tuple(colors) if colors is not None else None
        key = (surface, hsl_tuple, color_tuple)
        if key not in self.hsl_transforms:
            copy = surface.copy()
            transform_image_hsl(copy, hsl, colors)
            self.hsl_transforms[key] = copy

        return self.hsl_transforms[key]

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
