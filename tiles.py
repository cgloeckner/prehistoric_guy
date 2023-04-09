import pygame
import math
from dataclasses import dataclass

from constants import *
import resources
import platforms
import animations


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


class Renderer(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, cache: resources.Cache, surface: pygame.Surface, clock: pygame.time.Clock):
        self.cache = cache
        self.surface = surface
        self.clock = clock

        self.x = 0
        self.sprites = list()

        # load resources
        self.font = self.cache.get_font()
        self.background = self.cache.get_image('background')
        self.tiles = self.cache.get_image('tiles')
        self.objects = self.cache.get_image('objects')

    def draw_object(self, obj: platforms.Object) -> None:
        """Draw an object.
        """
        objects = self.objects
        if obj.hsl is not None:
            objects = self.cache.get_hsl_transformed(objects, obj.hsl)

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
        hsl = None
        if sprite.animation.hsl is not None:
            hsl = sprite.animation.hsl
        elif sprite.actor.hsl is not None:
            hsl = sprite.actor.hsl
        if hsl is not None:
            sprite_sheet = self.cache.get_hsl_transformed(sprite_sheet, hsl)

        # pos is bottom center, needs to be top left
        x = sprite.actor.x * WORLD_SCALE - SPRITE_SCALE // 2
        y = self.surface.get_height() - (sprite.actor.y * WORLD_SCALE + SPRITE_SCALE) - sprite.animation.delta_y

        x_offset = (0 if sprite.actor.face_x >= 0.0 else 1) * ANIMATION_NUM_FRAMES * SPRITE_SCALE
        clip = pygame.Rect(sprite.animation.frame_id * SPRITE_SCALE + x_offset,
                           sprite.animation.action_id * SPRITE_SCALE, SPRITE_SCALE, SPRITE_SCALE)
        self.surface.blit(sprite_sheet, (x, y), clip)

    def draw_ladder(self, ladder: platforms.Ladder, tileset_col: int) -> None:
        """Draw a ladder.
        """
        tiles = self.tiles
        # FIXME: allow for ladder coloring (see editor)

        # top left position
        x = ladder.x * WORLD_SCALE
        y = self.surface.get_height() - (ladder.y + 1) * WORLD_SCALE

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
        if platform.hsl is not None:
            tiles = self.cache.get_hsl_transformed(tiles, platform.hsl)

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

    def draw_projectile(self, proj: platforms.Projectile) -> None:
        """Draw a projectile.
        """
        # pos is centered, but needs to be top left
        x = proj.x * WORLD_SCALE - OBJECT_SCALE // 2
        y = self.surface.get_height() - (proj.y * WORLD_SCALE + OBJECT_SCALE // 2)

        variation_col = 0
        clip = pygame.Rect(variation_col * OBJECT_SCALE, proj.object_type * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE)

        angle = 2 * math.pi * proj.fly_ms / 360
        angle *= proj.spin_speed
        objects = self.cache.get_rotated_surface_clip(self.objects, clip, angle, flip=proj.face_x < 0.0)

        self.surface.blit(objects, (x, y))

    def draw(self, platformer: platforms.Physics, bg_col: int) -> None:
        # background
        self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        platformer.platforms.sort(key=lambda plat: plat.y)

        # FIXME: needs a better spot
        tileset_col = 0

        for p in platformer.platforms:
            self.draw_platform(p, tileset_col)

        for ladder in platformer.ladders:
            self.draw_ladder(ladder, tileset_col)

        for o in platformer.objects:
            self.draw_object(o)

        for s in self.sprites:
            self.draw_sprite(s)

        for proj in platformer.projectiles:
            self.draw_projectile(proj)

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.clock.get_fps()):02d}', False, 'white')
        self.surface.blit(fps_surface, (0, self.surface.get_height() - fps_surface.get_height()))
