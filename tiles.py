import pygame
from dataclasses import dataclass

import platforms
import animations
from constants import *


# tiles row offsets
PLATFORM_ROW: int = 0
TEXTURE_ROW: int = 2
LADDER_ROW: int = 3


@dataclass
class Sprite:
    # link to related actor
    actor: platforms.Actor
    # sprite frames
    sprite_sheet: pygame.Surface
    # animation related stuff
    animation: animations.Animation


def fill_pixels(surface: pygame.Surface, color: pygame.Color):
    """Replaces all non-transparent pixels with the given color.
    """
    pixels = pygame.PixelArray(surface)

    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if pixels[x, y] & 0xff000000 != 0:
                pixels[x, y] = color

    pixels.close()


class Renderer(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock):
        self.surface = surface
        self.clock = clock

        self.x = 0
        self.sprites = list()
        self.colored_cache = dict()

        # load resources
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 18)
        self.background = pygame.image.load('data/background.png')
        self.tiles = pygame.image.load('data/tiles.png')
        self.objects = pygame.image.load('data/objects.png')

    def get_colored_surface(self, surface: pygame.Surface, color: pygame.Color) -> pygame.Surface:
        """If not cached, a copy of the given surface is created and all non-transparent pixels are replaced with the
        given color. If cached, the existing copy is used.
        Returns the colored surface.
        """
        key = (surface, (color.r, color.g, color.b))
        if key in self.colored_cache:
            return self.colored_cache[key]

        copy = surface.copy()
        fill_pixels(copy, color)
        self.colored_cache[key] = copy

        return copy

    def draw_object(self, obj: platforms.Object) -> None:
        """Draw an object.
        """
        objects = self.objects
        if obj.color is not None:
            objects = self.get_colored_surface(objects, obj.color)

        # pos is bottom center, needs to be top left
        x = obj.x * WORLD_SCALE - OBJECT_SCALE // 2
        y = self.surface.get_height() - (obj.y * WORLD_SCALE + OBJECT_SCALE)

        variation_col = 0
        clip = (variation_col * OBJECT_SCALE, obj.object_type * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE)
        self.surface.blit(objects, (x, y), clip)

    def draw_sprite(self, sprite: Sprite) -> None:
        """Draw an actor's sprite.
        Note that all sprite sheet pixels are doubled (SPRITE_SCALE).
        """
        # color sprite with based on flashing animation (or else because of editor)
        sprite_sheet = sprite.sprite_sheet
        color = None
        if sprite.animation.color is not None:
            color = sprite.animation.color
        elif sprite.actor.color is not None:
            color = sprite.actor.color
        if color is not None:
            sprite_sheet = self.get_colored_surface(sprite_sheet, color)

        # pos is bottom center, needs to be top left
        x = sprite.actor.x * WORLD_SCALE - SPRITE_SCALE // 2
        y = self.surface.get_height() - (sprite.actor.y * WORLD_SCALE + SPRITE_SCALE)

        x_offset = (0 if sprite.actor.face_x >= 0.0 else 1) * ANIMATION_NUM_FRAMES * SPRITE_SCALE
        clip = pygame.Rect(sprite.animation.frame_id * SPRITE_SCALE + x_offset,
                           sprite.animation.action_id * SPRITE_SCALE, SPRITE_SCALE, SPRITE_SCALE)
        self.surface.blit(sprite_sheet, (x, y), clip)

    def draw_ladder(self, ladder: platforms.Ladder, tileset_col: int) -> None:
        """Draw a ladder.
        """
        tiles = self.tiles

        # top left position
        x = ladder.x * WORLD_SCALE
        y = self.surface.get_height() - (ladder.y + 1) * WORLD_SCALE

        w = WORLD_SCALE
        h = ladder.height * WORLD_SCALE

        # draw repeated ladder parts
        for i in range(ladder.height):
            self.surface.blit(tiles, (x, y - i * WORLD_SCALE),
                              ((3 * tileset_col + 1) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE,
                               WORLD_SCALE, WORLD_SCALE * 2))

        # draw upper ladder part
        self.surface.blit(tiles, (x, y - ladder.height * WORLD_SCALE),
                          ((3 * tileset_col) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))

        # draw lower ladder part
        self.surface.blit(tiles, (x, y + WORLD_SCALE),
                          ((3 * tileset_col + 2) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))

    def draw_platform(self, platform: platforms.Platform, tileset_col: int) -> None:
        """Draw a platform.
        """
        tiles = self.tiles
        if platform.color is not None:
            tiles = self.get_colored_surface(tiles, platform.color)

        x = platform.x * WORLD_SCALE
        y = self.surface.get_height() - platform.y * WORLD_SCALE

        for i in range(int(platform.width)):
            # draw texture below
            for j in range(int(platform.height)):
                self.surface.blit(tiles,
                                  (x + i * WORLD_SCALE, y + j * WORLD_SCALE),
                                  ((3 * tileset_col+1) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))

            # draw platform on top
            self.surface.blit(tiles,
                              (x + i * WORLD_SCALE, y - WORLD_SCALE),
                              ((3 * tileset_col+1) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                               WORLD_SCALE, WORLD_SCALE * 2))

        if platform.height > 0.0:
            # draw texture edges
            for j in range(int(platform.height)):
                self.surface.blit(tiles,
                                  (x - WORLD_SCALE, y + j * WORLD_SCALE),
                                  (3 * tileset_col * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))
                self.surface.blit(tiles,
                                  (x + int(platform.width) * WORLD_SCALE, y + j * WORLD_SCALE),
                                  ((3 * tileset_col + 2) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))

        # draw platform edges
        self.surface.blit(tiles,
                          (x - WORLD_SCALE, y - WORLD_SCALE),
                          (3 * tileset_col * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))
        self.surface.blit(tiles,
                          (x + int(platform.width) * WORLD_SCALE, y - WORLD_SCALE),
                          ((3 * tileset_col + 2) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))

    def draw(self, platformer: platforms.Physics, bg_col: int) -> None:
        # background
        self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        platformer.platforms.sort(key=lambda plat: plat.y)

        # FIXME: needs a better spot
        tileset_col = 0

        for p in platformer.platforms:
            self.draw_platform(p, tileset_col)

        for l in platformer.ladders:
            self.draw_ladder(l, tileset_col)

        for o in platformer.objects:
            self.draw_object(o)

        for s in self.sprites:
            self.draw_sprite(s)

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.clock.get_fps()):02d}', False, 'white')
        self.surface.blit(fps_surface, (0, self.surface.get_height() - fps_surface.get_height()))
