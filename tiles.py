import pygame
import pygame.gfxdraw
from dataclasses import dataclass

import platforms
import animations
from constants import *


# tiles row offsets
PLATFORM_ROW: int = 0
TEXTURE_ROW: int = 2
STAIRS_ROW: int = 3


@dataclass
class Sprite:
    sprite_sheet: pygame.Surface
    flipped_sheet: pygame.Surface
    actor: platforms.Actor
    animation: animations.Animation


class Renderer(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, debug_render: bool = False):
        self.surface = surface
        self.clock = clock
        self.debug_render = debug_render

        self.x = 0
        self.sprites = list()

        # load resources
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 18)
        self.background = pygame.image.load('data/background.png')
        self.tiles = pygame.image.load('data/tiles.png')
        self.objects = pygame.image.load('data/objects.png')

    def draw_object(self, obj: platforms.Object) -> None:
        x = obj.pos_x * WORLD_SCALE
        y = self.surface.get_height() - obj.pos_y * WORLD_SCALE

        if self.debug_render:
            # draw hit box
            pygame.gfxdraw.circle(self.surface, int(x + WORLD_SCALE // 4), int(y + WORLD_SCALE // 4),
                                  int(0.25 * WORLD_SCALE), pygame.Color('gold'))

        variation_col = 0
        clip = (variation_col * OBJECT_SCALE, obj.object_type * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE)
        self.surface.blit(self.objects, (x, y), clip)

    def draw_actor(self, sprite: Sprite) -> None:
        """Draw an actor's sprite.
        Note that all sprite sheet pixels are doubled.
        """
        x = sprite.actor.pos_x * WORLD_SCALE
        y = self.surface.get_height() - sprite.actor.pos_y * WORLD_SCALE

        if self.debug_render:
            # draw hit box
            pygame.gfxdraw.circle(self.surface, int(x), int(y - sprite.actor.radius * WORLD_SCALE),
                                  int(sprite.actor.radius * WORLD_SCALE), pygame.Color('red'))

        x -= SPRITE_SCALE // 2
        y -= SPRITE_SCALE
        clip = pygame.Rect(sprite.animation.frame_id * SPRITE_SCALE, sprite.animation.action_id * SPRITE_SCALE,
                           SPRITE_SCALE, SPRITE_SCALE)
        sprite_sheet = sprite.sprite_sheet
        if sprite.actor.face_x < 0:
            sprite_sheet = sprite.flipped_sheet
        self.surface.blit(sprite_sheet, (x, y), clip)

    def draw_platform(self, platform: platforms.Platform, tileset_col: int) -> None:
        x = platform.x * WORLD_SCALE
        y = self.surface.get_height() - platform.y * WORLD_SCALE

        for i in range(int(platform.width)):
            # draw texture below
            for j in range(int(platform.height)):
                self.surface.blit(self.tiles,
                                  (x + i * WORLD_SCALE, y + j * WORLD_SCALE),
                                  ((3 * tileset_col+1) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))

            # draw platform on top
            self.surface.blit(self.tiles,
                              (x + i * WORLD_SCALE, y - WORLD_SCALE),
                              ((3 * tileset_col+1) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                               WORLD_SCALE, WORLD_SCALE * 2))

        if platform.height > 0.0:
            # draw texture edges
            for j in range(int(platform.height)):
                self.surface.blit(self.tiles,
                                  (x - WORLD_SCALE, y + j * WORLD_SCALE),
                                  (3 * tileset_col * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))
                self.surface.blit(self.tiles,
                                  (x + int(platform.width) * WORLD_SCALE, y + j * WORLD_SCALE),
                                  ((3 * tileset_col + 2) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE,
                                   WORLD_SCALE, WORLD_SCALE))

        # draw platform edges
        self.surface.blit(self.tiles,
                          (x - WORLD_SCALE, y - WORLD_SCALE),
                          (3 * tileset_col * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))
        self.surface.blit(self.tiles,
                          (x + int(platform.width) * WORLD_SCALE, y - WORLD_SCALE),
                          ((3 * tileset_col + 2) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE * 2))

        if self.debug_render:
            # draw hit box
            x2 = (platform.x + platform.width) * WORLD_SCALE
            y2 = self.surface.get_height() - (platform.y - platform.height) * WORLD_SCALE
            pygame.draw.lines(self.surface, 'red', False, ((x, y2), (x, y), (x2, y), (x2, y2)))

    def draw(self, platformer: platforms.Physics, bg_col: int) -> None:
        # background
        self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        platformer.platforms.sort(key=lambda plat: plat.y)

        for p in platformer.platforms:
            self.draw_platform(p, 0)

        for o in platformer.objects:
            self.draw_object(o)

        for s in self.sprites:
            self.draw_actor(s)

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.clock.get_fps()):02d}', False, 'white')
        self.surface.blit(fps_surface, (0, self.surface.get_height() - fps_surface.get_height()))