import pygame
import pathlib
from typing import Dict, Tuple, List, Optional

from core import constants, paths


def transform_color_replace(surface: pygame.Surface, color_str_dict: Dict[str, str]) -> None:
    """Rotates a surface's colors in place. Only pixels are modified whose color is in the given list. The alteration
    is based on the given delta tuple: hue, saturation, lightness. Transparent pixels are ignored.
    """
    pixels = pygame.PixelArray(surface)
    mapping = dict()
    for color_str in color_str_dict:
        mapping[tuple(pygame.Color(color_str))] = pygame.Color(color_str_dict[color_str])

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 == 0:
                continue

            color_key = tuple(surface.unmap_rgb(pixels[x, y]))
            if color_key in mapping:
                pixels[x, y] = mapping[color_key]

    pixels.close()


def flip_sprite_sheet(src: pygame.Surface, tile_size: int) -> pygame.Surface:
    """Splits all sprite frames but keeps the logical order of the entire sprite sheet.
    A new sprite sheet is returned which holds all sprites (left: original, right: flipped frames).
    """
    size = src.get_size()
    mirrored = pygame.transform.flip(src, flip_x=True, flip_y=False)
    dst = pygame.Surface((size[0] * 2, size[1]), flags=pygame.SRCALPHA)

    dst.blit(src, (0, 0))
    for column in range(src.get_width() // tile_size):
        dst.blit(mirrored, (size[0] + column * tile_size, 0), (size[0] - (column + 1) * tile_size, 0, tile_size,
                                                               size[1]))

    return dst


def fill_pixels(surface: pygame.Surface, color: pygame.Color):
    """Replaces all non-transparent pixels with the given color in place."""
    pixels = pygame.PixelArray(surface)

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 != 0:
                pixels[x, y] = color

    pixels.close()


def add_outline(surface: pygame.Surface, color: pygame.Color):
    """Adds a thin outline around each non-transparent pixel without enlarging the art."""
    pixels = pygame.PixelArray(surface)
    w, h = surface.get_size()
    mask = pygame.mask.from_surface(surface)

    for y in range(h):
        for x in range(w):
            if mask.get_at((x, y)) == 0:
                continue

            if x-1 >= 0 and mask.get_at((x-1, y)) == 0 or \
                x+1 < w and mask.get_at((x+1, y)) == 0 or \
                y-1 >= 0 and mask.get_at((x, y-1)) == 0 or \
                y+1 < h and mask.get_at((x, y+1)) == 0:
                pixels[x, y] = color

    pixels.close()


COLOR_TUPLE = Tuple[int, int, int]
RECT_TUPLE = Tuple[int, int, int, int]
HSL_TUPLE = Tuple[float, float, float]


class Cache(object):
    """Caches resources and eventually loads the image from a root directory.
    All images are supposed to be in PNG format with the file extension .png"""

    def __init__(self, data_paths: paths.DataPath):
        """Initializes the cache with the given root directory.
        """
        self.paths = data_paths

        # regular resources
        self.images: Dict[str, pygame.Surface] = dict()
        self.fonts: Dict[str, pygame.font.Font] = dict()

        # sprites include their flipped frames
        self.sprites: Dict[Tuple[str, COLOR_TUPLE], pygame.Surface] = dict()

        # hsl-transformed and rotated surfaces
        self.hsl_transforms: Dict[Tuple[pygame.Surface, HSL_TUPLE, Optional[COLOR_TUPLE]]] = dict()
        self.rotated: Dict[Tuple[pygame.Surface, RECT_TUPLE, bool], List[pygame.Surface]] = dict()

    def get_image(self, path: pathlib.Path) -> pygame.Surface:
        """Loads the image via filename. If already loaded, it's taken from the cache. Returns the image's surface."""
        filename = str(path)
        if filename not in self.images:
            surface = pygame.image.load(filename)
            if constants.DOES_SCALE_2X:
                surface = pygame.transform.scale_by(surface, 2)
            self.images[filename] = surface.convert_alpha()

        return self.images[filename]

    def get_sprite_sheet(self, path: pathlib.Path, outline_color: Optional[pygame.Color] = None) -> pygame.Surface:
        """Adds the x-flipped sprites into the sprite sheet. Returns the finished sheet."""
        filename = str(path)
        color_tuple = tuple(outline_color) if outline_color is not None else None
        key = (filename, color_tuple)
        if key not in self.sprites:
            image = self.get_image(path)
            surface = flip_sprite_sheet(image, constants.SPRITE_SCALE)
            if outline_color is not None:
                add_outline(surface, outline_color)

            self.sprites[key] = surface

        return self.sprites[key]

    def get_font(self, fontname: str = '', font_size: int = 18) -> pygame.font.Font:
        """Loads a SysFont via filename and size. Returns the font object."""
        if fontname == '':
            return pygame.font.SysFont(pygame.font.get_default_font(), font_size)

        # FIXME: implement font loading
        raise NotImplementedError()

    def get_rotated_surface_clip(self, surface: pygame.Surface, rect: pygame.Rect, angle: float, flip: bool)\
            -> pygame.Surface:
        # noinspection GrazieInspection
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
