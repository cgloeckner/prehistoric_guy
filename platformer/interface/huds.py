import pygame
from enum import IntEnum

from core import constants, resources, ui
from platformer import physics, characters, renderer, controls


# HUD tileset columns
class HudType(IntEnum):
    HEART = 0
    WEAPON = 1


class HudSystem:
    def __init__(self, players_context: controls.PlayersContext, physics_context: physics.Context,
                 characters_context: characters.Context, target: pygame.Surface, cache: resources.Cache,
                 camera: renderer.Camera):
        self.players_context = players_context
        self.physics_context = physics_context
        self.characters_context = characters_context
        self.camera = camera

        self.target = target
        self.cache = cache

        hud_path = cache.paths('hud', 'png')
        self.tileset = cache.get_image(hud_path)

    def draw_icons(self, actor: characters.Actor) -> None:
        # draw heart icon per hit point
        hud_clip = pygame.Rect(0 * constants.OBJECT_SCALE, HudType.HEART * constants.OBJECT_SCALE,
                               constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        for i in range(actor.hit_points.value):
            self.target.blit(self.tileset, (i * constants.OBJECT_SCALE, 0), hud_clip)

        # draw weapon icon per axe
        weapon_clip = pygame.Rect(0 * constants.OBJECT_SCALE, HudType.WEAPON * constants.OBJECT_SCALE,
                                  constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        for i in range(actor.num_axes.value):
            self.target.blit(self.tileset, (i * constants.OBJECT_SCALE, constants.OBJECT_SCALE), weapon_clip)

    def draw_hud(self, actor: controls.Player):
        char_actor = self.characters_context.actors.get_by_id(actor.object_id)
        self.draw_icons(char_actor)

        phys_actor = self.physics_context.actors.get_by_id(actor.object_id)

        # FIXME needs Renderer's method instead to account for scale
        screen_pos = self.camera.from_world_coord(phys_actor.pos)
        screen_pos *= constants.WORLD_SCALE

    def draw(self):
        for actor in self.players_context.actors:
            self.draw_hud(actor)
