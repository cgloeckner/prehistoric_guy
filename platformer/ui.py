import pygame
from dataclasses import dataclass

from core.constants import *
import core.resources as resources

import platformer.physics as physics
import platformer.render as render
import platformer.characters as characters


HEART_HUD: int = 0
WEAPON_HUD: int = 1


@dataclass
class Hud:
    object_id: int


def progress_bar(target: pygame.Surface, x: int, y: int, width: int, height: int, progress: float,
                 border_width: int = 1, box_color: pygame.Color = pygame.Color('black'),
                 bar_color: pygame.Color = pygame.Color('white'), centered: bool = True) -> None:
    if centered:
        x -= (width + 2 * border_width) // 2
        y -= (height + 2 * border_width) // 2

    pygame.draw.rect(target, box_color, (x, y, width + 2 * border_width, height + 2 * border_width))
    pygame.draw.rect(target, bar_color, (x+1, y+1, width * progress, height))


class PlayerHuds(object):
    def __init__(self, phys_system: physics.Physics, render_system: render.Renderer, char_system: characters.Characters,
                 cache: resources.Cache):
        self.phys_system = phys_system
        self.render_system = render_system
        self.char_system = char_system
        self.cache = cache
        self.tileset = cache.get_image('hud')

        self.player_ids = list()

    def draw_icons(self, char_actor: characters.Actor) -> None:
        for i in range(char_actor.hit_points):
            self.render_system.target.blit(self.tileset, (i * OBJECT_SCALE, 0),
                                           (0 * OBJECT_SCALE, HEART_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))

        for i in range(char_actor.num_axes):
            self.render_system.target.blit(self.tileset, (i * OBJECT_SCALE, OBJECT_SCALE),
                                           (0 * OBJECT_SCALE, WEAPON_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))

    def draw_throw_progress(self, char_actor: characters.Actor, value: float) -> None:
        phys_actor = self.phys_system.get_by_id(char_actor.object_id)

        pos = self.render_system.world_to_screen_coord(phys_actor.x, phys_actor.y)
        pos.y += WORLD_SCALE

        progress_bar(self.render_system.target, pos, 15, 3, value)

    def update(self, elapsed_ms: int) -> None:
        pass

    def draw(self) -> None:
        for object_id in self.player_ids:
            char_actor = self.char_system.try_get_by_id(object_id)
            if char_actor is None:
                continue

            self.draw_icons(char_actor)

            # FIXME: query controls -> get_throwing_process() and draw_throw_progress(char_actor, value)
