import pygame

from platformer.constants import *
import platformer.controls as controls

HEART_HUD: int = 0
WEAPON_HUD: int = 1


def hud_icons(target: pygame.Surface, tileset: pygame.Surface, c: controls.Character) -> None:
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


def throw_progress(target: pygame.Surface, camera: pygame.Rect, c: controls.Character, throw_perc: float) -> None:
    progress_bar(target, int(c.sprite.actor.x * WORLD_SCALE) - camera.x,
                 RESOLUTION_Y - (-camera.y + int(c.sprite.actor.y * WORLD_SCALE + WORLD_SCALE)),
                 15, 3, throw_perc)
