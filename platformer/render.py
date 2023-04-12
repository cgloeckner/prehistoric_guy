import pygame
import pygame.gfxdraw
import math
from dataclasses import dataclass
from typing import List

from core.constants import *
from core import resources

from platformer import camera
from platformer import animations
from platformer import physics


@dataclass
class Actor:
    object_id: int
    # sprite frames
    sprite_sheet: pygame.Surface


class Renderer(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, phys_system: physics.Physics, ani_system: animations.Animating, cache: resources.Cache,
                 cam: camera.Camera):
        """
        :param phys_system: Physics System to fetch data from
        :param ani_system: Animations System to fetch data from
        :param cache: Resource Cache to acquire images from
        :param cam: Camera used to draw
        """
        self.phys_system = phys_system
        self.ani_system = ani_system
        self.cache = cache
        self.camera = cam

        self.tileset_col = 0
        self.sprites: List[Actor] = list()

        # load resources
        self.background = self.cache.get_image('background')
        self.tiles = self.cache.get_image('tiles')
        self.objects = self.cache.get_image('objects')

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the sprite who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.sprites if a.object_id == object_id][0]

    def draw_object(self, obj: physics.Object) -> None:
        """Draw an object.
        """
        objects = self.objects
        if obj.hsl is not None:
            objects = self.cache.get_hsl_transformed(objects, obj.hsl)

        pos, clip = self.camera.get_object_rects(obj)

        self.camera.buffer.blit(objects, pos, clip)

    def draw_sprite(self, sprite: Actor) -> None:
        """Draw an actor's sprite.
        Note that all sprite sheet pixels are doubled (SPRITE_SCALE).
        """
        # color sprite with based on flashing animation (or else because of editor)
        sprite_sheet = sprite.sprite_sheet
        phys_data = self.phys_system.get_by_id(sprite.object_id)
        ani_data = self.ani_system.get_by_id(sprite.object_id)
        hsl = None
        if ani_data.hsl is not None:
            hsl = ani_data.hsl
        elif phys_data.hsl is not None:
            hsl = phys_data.hsl
        if hsl is not None:
            sprite_sheet = self.cache.get_hsl_transformed(sprite_sheet, hsl)

        pos, clip = self.camera.get_actor_rects(phys_data, ani_data)
        pos.y += ani_data.delta_y

        self.camera.buffer.blit(sprite_sheet, (pos.x, pos.y), clip)

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        """Draw a ladder.
        """
        tiles = self.tiles
        if ladder.hsl is not None:
            tiles = self.cache.get_hsl_transformed(tiles, ladder.hsl)

        pos, top_clip, mid_clip, bottom_clip = self.camera.get_ladder_rects(ladder, self.tileset_col)

        # draw upper part of the ladder
        self.camera.buffer.blit(tiles, pos, top_clip)

        # draw ladder elements
        for i in range(ladder.height):
            self.camera.buffer.blit(tiles, pos, mid_clip)
            pos.y += WORLD_SCALE

        # draw lower part of the ladder:
        self.camera.buffer.blit(tiles, pos, bottom_clip)

    def draw_platform(self, platform: physics.Platform) -> None:
        """Draw a platform.
        """
        tiles = self.tiles
        if platform.hsl is not None:
            tiles = self.cache.get_hsl_transformed(tiles, platform.hsl)

        pos, left, plat, right, tex = self.camera.get_platform_rects(platform, self.tileset_col)
        pos.y -= WORLD_SCALE  # pos is returned top left
        pos_copy = pos.copy()

        # draw textures
        for y in range(platform.height):
            pos.x = pos_copy.x
            for x in range(platform.width):
                self.camera.buffer.blit(tiles, pos, tex)
                pos.x += WORLD_SCALE
            pos.y -= WORLD_SCALE

        # draw platform
        pos = pos_copy.copy()
        for x in range(platform.width):
            self.camera.buffer.blit(tiles, pos, plat)
            pos.x += WORLD_SCALE

        # draw edges
        pos = pos_copy.copy()
        pos.x -= WORLD_SCALE
        self.camera.buffer.blit(tiles, pos, left)
        pos.x += 2 * WORLD_SCALE
        self.camera.buffer.blit(tiles, pos, right)

    def draw_projectile(self, proj: physics.Projectile) -> None:
        """Draw a projectile.
        """
        pos, clip = self.camera.get_projectile_rects(proj)

        angle = 2 * math.pi * proj.fly_ms / 360
        angle *= proj.spin_speed
        objects = self.cache.get_rotated_surface_clip(self.objects, clip, angle, flip=proj.face_x < 0.0)

        self.camera.buffer.blit(objects, pos)

    def update(self, elapsed_ms: int) -> None:
        pass

    def draw(self) -> None:
        # background
        # FIXME: needs a better solution (also artistically) to work with the camera implementation
        # self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        self.phys_system.platforms.sort(key=lambda plat: plat.y)

        for p in self.phys_system.platforms:
            self.draw_platform(p)

        for ladder in self.phys_system.ladders:
            self.draw_ladder(ladder)

        for o in self.phys_system.objects:
            self.draw_object(o)

        for s in self.sprites:
            self.draw_sprite(s)

        for proj in self.phys_system.projectiles:
            self.draw_projectile(proj)

    def draw_hitboxes(self) -> None:
        """Performs debug drawing of shapes.
        """
        for platform in self.phys_system.platforms:
            pos = self.camera.get_platform_rects(platform)[0]
            pos.h *= -1
            pygame.gfxdraw.rectangle(self.camera.buffer, pos, pygame.Color('red'))

        for ladder in self.phys_system.ladders:
            pos = self.camera.get_ladder_rects(ladder)[0]
            pygame.gfxdraw.rectangle(self.camera.buffer, pos, pygame.Color('blue'))

        for obj in self.phys_system.objects:
            pos = self.camera.get_object_rects(obj)[0]
            pygame.gfxdraw.circle(self.camera.buffer, *pos.center, int(physics.OBJECT_RADIUS * WORLD_SCALE),
                                  pygame.Color('gold'))

        for actor in self.phys_system.actors:
            x, y = self.camera.get_actor_pos(actor).center
            y = int(y + actor.radius * WORLD_SCALE)
            pygame.gfxdraw.circle(self.camera.buffer, x, y, int(actor.radius * WORLD_SCALE),
                                  pygame.Color('green'))

        for proj in self.phys_system.projectiles:
            pos = self.camera.get_projectile_rects(proj)[0]
            pygame.gfxdraw.circle(self.camera.buffer, *pos.center, int(proj.radius * WORLD_SCALE),
                                  pygame.Color('orange'))
