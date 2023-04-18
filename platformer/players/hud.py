import pygame
from enum import IntEnum

from core import constants, ui
from platformer import characters

from . controls import Actor


# HUD tileset columns
class HudType(IntEnum):
    HEART = 0
    WEAPON = 1


def draw_icons(target: pygame.Surface, tileset: pygame.Surface, char_actor: characters.Actor) -> None:
    for i in range(char_actor.hit_points.value):
        target.blit(tileset, (i * constants.OBJECT_SCALE, 0),
                             (0 * constants.OBJECT_SCALE, HudType.HEART * constants.OBJECT_SCALE,
                              constants.OBJECT_SCALE, constants.OBJECT_SCALE))

    for i in range(char_actor.num_axes.value):
        target.blit(tileset, (i * constants.OBJECT_SCALE, constants.OBJECT_SCALE),
                             (0 * constants.OBJECT_SCALE, HudType.WEAPON * constants.OBJECT_SCALE,
                              constants.OBJECT_SCALE, constants.OBJECT_SCALE))


def draw_throw_progress(target: pygame.Surface, screen_pos: pygame.math.Vector2, control_actor: Actor) -> None:
    value = control_actor.state.get_throwing_progress()
    ui.progress_bar(target, screen_pos.x, screen_pos.y, 15, 3, value)
