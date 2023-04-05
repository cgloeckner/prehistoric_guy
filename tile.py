import pygame
import random

from platform import Platformer, Actor, Object, Platform


RESOLUTION_X: int = 320
RESOLUTION_Y: int = 240
WORLD_SCALE: int = RESOLUTION_X // 10
OBJECT_SCALE: int = WORLD_SCALE // 2

# tiles row offsets
PLATFORM_ROW: int = 0
TEXTURE_ROW: int = 2


class Tiling(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, debug_render: bool = False):
        self.surface = surface
        self.clock = clock
        self.debug_render = debug_render

        self.x = 0

        # load resources
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 18)
        self.background = pygame.image.load('data/background.png')
        self.tiles = pygame.image.load('data/tiles.png')
        self.objects = pygame.image.load('data/objects.png')

    def draw_actor(self, actor: Actor) -> None:
        # FIXME: replace debug rendering
        pos = (actor.pos_x * WORLD_SCALE,
               self.surface.get_height() - actor.pos_y * WORLD_SCALE - actor.radius * WORLD_SCALE)
        pygame.draw.circle(self.surface, 'blue', pos, actor.radius * WORLD_SCALE)

    def draw_object(self, obj: Object) -> None:
        # FIXME: replace debug rendering
        """"
        pos = (obj.pos_x * WORLD_SCALE,
               self.surface.get_height() - obj.pos_y * WORLD_SCALE)
        pygame.draw.circle(self.surface, 'gold', pos, 0.25 * WORLD_SCALE)
        """
        x = obj.pos_x * WORLD_SCALE
        y = self.surface.get_height() - obj.pos_y * WORLD_SCALE

        variation_col = 0
        self.surface.blit(self.objects,
                          (x, y),
                          (variation_col * OBJECT_SCALE, obj.object_type * OBJECT_SCALE,
                           OBJECT_SCALE, OBJECT_SCALE))

    def draw_platform(self, platform: Platform, tileset_col: int) -> None:
        x = platform.x * WORLD_SCALE
        y = self.surface.get_height() - platform.y * WORLD_SCALE

        set_col = 0
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
            x2 = (platform.x + platform.width) * WORLD_SCALE
            y2 = self.surface.get_height() - (platform.y - platform.height) * WORLD_SCALE
            pygame.draw.line(self.surface, 'red', (x, y), (x2, y), 4)
            pygame.draw.line(self.surface, 'red', (x, y), (x, y2), 4)
            pygame.draw.line(self.surface, 'red', (x2, y), (x2, y2), 4)

    def draw(self, platformer: Platformer, bg_col: int) -> None:
        # background
        self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        platformer.platforms.sort(key=lambda plat: plat.y)

        for p in platformer.platforms:
            self.draw_platform(p, 0)

        for o in platformer.objects:
            self.draw_object(o)

        for a in platformer.actors:
            self.draw_actor(a)

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.clock.get_fps()):02d}', False, 'white')
        self.surface.blit(fps_surface, (0, self.surface.get_height() - fps_surface.get_height()))
