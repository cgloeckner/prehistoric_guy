import pygame

from platform import Platformer, Actor, Platform


RESOLUTION_X: int = 320
RESOLUTION_Y: int = 240
WORLD_SCALE: int = RESOLUTION_X // 10


class Tiling(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, surface: pygame.Surface, clock: pygame.time.Clock, debug_render: bool = False):
        self.surface = surface
        self.clock = clock
        self.debug_render = debug_render

        # load resources
        self.font = pygame.font.SysFont(pygame.font.get_default_font(), 18)
        self.background = pygame.image.load('data/day.png')
        self.tile = pygame.image.load('data/dirt.png')

    def draw_actor(self, actor: Actor) -> None:
        # FIXME: replace debug rendering
        pos = (actor.pos_x * WORLD_SCALE,
               self.surface.get_height() - actor.pos_y * WORLD_SCALE - actor.radius * WORLD_SCALE)
        pygame.draw.circle(self.surface, 'blue', pos, actor.radius * WORLD_SCALE)

    def draw_platform(self, platform: Platform) -> None:
        x = platform.x * WORLD_SCALE
        y = self.surface.get_height() - platform.y * WORLD_SCALE

        for i in range(int(platform.width)):
            self.surface.blit(self.tile, (x + i * WORLD_SCALE, y), (0, 0, WORLD_SCALE, WORLD_SCALE))
            for j in range(int(platform.height)):
                self.surface.blit(self.tile, (x + i * WORLD_SCALE,
                                              y + (j+1) * WORLD_SCALE), (0, WORLD_SCALE, WORLD_SCALE, WORLD_SCALE))

        if self.debug_render:
            x2 = (platform.x + platform.width) * WORLD_SCALE
            y2 = self.surface.get_height() - (platform.y - platform.height) * WORLD_SCALE
            pygame.draw.line(self.surface, 'red', (x, y), (x2, y), 4)
            pygame.draw.line(self.surface, 'red', (x, y), (x, y2), 4)
            pygame.draw.line(self.surface, 'red', (x2, y), (x2, y2), 4)

    def draw(self, platformer: Platformer) -> None:
        # tiled background
        bg_size = self.background.get_size()
        num_w = RESOLUTION_X // bg_size[0] + 1
        num_h = RESOLUTION_Y // bg_size[1] + 1
        for y in range(num_h):
            for x in range(num_w):
                self.surface.blit(self.background, (x * bg_size[0], y * bg_size[1]), (0, 0, bg_size[0], bg_size[1]))

        # foreground
        platformer.platforms.sort(key=lambda plat: plat.y)
        for p in platformer.platforms:
            self.draw_platform(p)
        for a in platformer.actors:
            self.draw_actor(a)

        # draw FPS
        if self.debug_render:
            fps_surface = self.font.render(f'FPS: {int(self.clock.get_fps()):02d}', False, 'white')
            self.surface.blit(fps_surface, (0, self.surface.get_height() - fps_surface.get_height()))
