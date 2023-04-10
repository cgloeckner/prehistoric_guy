import pygame

from core.constants import *

import platformer.physics as physics
import platformer.characters as characters


HEART_HUD: int = 0
WEAPON_HUD: int = 1


# FIXME: add Hud class, rename file to ui.py


def hud_icons(target: pygame.Surface, tileset: pygame.Surface, c: characters.Actor) -> None:
    for i in range(c.hit_points):
        target.blit(tileset, (i * OBJECT_SCALE, 0),
                    (0 * OBJECT_SCALE, HEART_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))

    for i in range(c.num_axes):
        target.blit(tileset, (i * OBJECT_SCALE, OBJECT_SCALE),
                    (0 * OBJECT_SCALE, WEAPON_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))


def progress_bar(target: pygame.Surface, x: int, y: int, width: int, height: int, progress: float,
                 border_width: int = 1, box_color: pygame.Color = pygame.Color('black'),
                 bar_color: pygame.Color = pygame.Color('white'), centered: bool = True) -> None:
    if centered:
        x -= (width + 2 * border_width) // 2
        y -= (height + 2 * border_width) // 2

    pygame.draw.rect(target, box_color, (x, y, width + 2 * border_width, height + 2 * border_width))
    pygame.draw.rect(target, bar_color, (x+1, y+1, width * progress, height))


def throw_progress(target: pygame.Surface, camera: pygame.Rect, phys_actor: physics.Actor, throw_perc: float) -> None:
    progress_bar(target, int(phys_actor.x * WORLD_SCALE) - camera.x,
                 RESOLUTION_Y - (-camera.y + int(phys_actor.y * WORLD_SCALE + WORLD_SCALE)),
                 15, 3, throw_perc)
