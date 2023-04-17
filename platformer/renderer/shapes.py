import pygame
import pygame.gfxdraw
from dataclasses import dataclass

from core import constants

from platformer import physics
from platformer.renderer import base


@dataclass
class Mapping:
    platform: str = 'red'
    ladder: str = 'yellow'
    object: str = 'blue'
    actor: str = 'green'
    projectile: str = 'red'


class ShapeRenderer(base.Renderer):

    def __init__(self, camera: base.Camera, target: pygame.Surface, physics_context: physics.Context):
        super().__init__(camera)
        self.target = target
        self.physics_context = physics_context
        self.mapping = Mapping()

    def from_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Translates world coordinates into screen coordinates.
        In world coordinates, y leads from bottom to top (0,0 as bottom left).
        In screen coordinates, y leads from top to bottom (0,0 as top left).
        Returns a vector of integer coordinates.
        """
        p = self.camera.from_world_coord(pos.copy())
        p *= constants.WORLD_SCALE
        p.x = int(p.x)
        p.y = int(self.camera.height - p.y)
        return p

    def to_world_coord(self, pos: pygame.math.Vector2) -> pygame.math.Vector2:
        """Translates screen coordinates into world coordinates.
        Returns a vector of float coordinates.
        """
        p = pos.copy()
        p.y = self.target.get_height() - p.y
        p /= constants.WORLD_SCALE
        p = self.camera.to_world_coord(p)
        return p

    def get_platform_rect(self, platform: physics.Platform) -> pygame.Rect:
        """Returns the positioning rect.
        """
        pos_rect = pygame.Rect(0, 0, platform.width * constants.WORLD_SCALE, platform.height * constants.WORLD_SCALE)
        pos_rect.topleft = self.from_world_coord(platform.pos)

        return pos_rect

    def get_ladder_rect(self, ladder: physics.Ladder) -> pygame.Rect:
        """Returns the positioning rect.
        """
        pos_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, ladder.height * constants.WORLD_SCALE)
        pos_rect.midbottom = self.from_world_coord(ladder.pos)

        return pos_rect

    def get_object_rect(self, obj: physics.Object) -> pygame.Rect:
        """Returns the positioning and clipping rectangles.
        """
        # FIXME: make more flexible
        variation_col = 0

        pos_rect = pygame.Rect(0, 0, constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        pos_rect.midbottom = self.from_world_coord(obj.pos)

        return pos_rect

    def get_actor_rect(self, actor: physics.Actor) -> pygame.Rect:
        """Returns the positioning rect.
        """
        pos_rect = pygame.Rect(0, 0, constants.SPRITE_SCALE, constants.SPRITE_SCALE)
        pos_rect.midbottom = self.from_world_coord(actor.pos)

        return pos_rect

    def get_projectile_rect(self, proj: physics.Projectile) -> pygame.Rect:
        """Returns the positioning rect.
        """
        # FIXME: make more flexible
        variation_col = 0

        pos_rect = pygame.Rect(0, 0, constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        pos_rect.center = self.from_world_coord(proj.pos)

        return pos_rect

    def update(self, elapsed_ms: int) -> None:
        pass

    def draw_platform(self, platform: physics.Platform) -> None:
        pos = self.get_platform_rect(platform)
        pos.h *= -1
        pygame.gfxdraw.rectangle(self.target, pos, pygame.Color(self.mapping.platform))

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        pos = self.get_ladder_rect(ladder)
        pygame.gfxdraw.rectangle(self.target, pos, pygame.Color(self.mapping.ladder))

    def draw_object(self, obj: physics.Object) -> None:
        pos = self.get_object_rect(obj)
        r = int(physics.OBJECT_RADIUS * constants.WORLD_SCALE)
        c = pygame.Color(self.mapping.object)
        pygame.gfxdraw.circle(self.target, *pos.center, r, c)

    def draw_actor(self, actor: physics.Actor) -> None:
        x, y = self.get_actor_rect(actor).center
        y = int(y + actor.radius * constants.WORLD_SCALE)
        r = int(actor.radius * constants.WORLD_SCALE)
        c = pygame.Color(self.mapping.actor)
        pygame.gfxdraw.circle(self.target, x, y, r, c)

    def draw_projectile(self, proj: physics.Projectile) -> None:
        pos = self.get_projectile_rect(proj)
        r = int(proj.radius * constants.WORLD_SCALE)
        c = pygame.Color(self.mapping.projectile)
        pygame.gfxdraw.circle(self.target, *pos.center, r, c)

    def draw(self) -> None:
        for platform in self.physics_context.platforms:
            self.draw_platform(platform)

        for ladder in self.physics_context.ladders:
            self.draw_ladder(ladder)

        for obj in self.physics_context.objects:
            self.draw_object(obj)

        for projectile in self.physics_context.projectiles:
            self.draw_projectile(projectile)

        for actor in self.physics_context.actors:
            self.draw_actor(actor)
