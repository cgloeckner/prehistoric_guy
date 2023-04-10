import pygame
import math
from dataclasses import dataclass

from platformer.constants import *
import platformer.animations as animations
import platformer.physics as physics
import platformer.resources as resources

# tiles row offsets
PLATFORM_ROW: int = 0
TEXTURE_ROW: int = 2
LADDER_ROW: int = 3


@dataclass
class Actor:
    object_id: int
    # sprite frames
    sprite_sheet: pygame.Surface


class Renderer(object):
    """Handles drawing the tiled environment.
    """
    def __init__(self, phys_system: physics.Physics, ani_system: animations.Animating, cache: resources.Cache,
                 target: pygame.Surface):
        """
        :param phys_system: Physics System to fetch data from
        :param ani_system: Animations System to fetch data from
        :param cache: Resource Cache to acquire images from
        :param target: Rendering target
        """
        self.phys_system = phys_system
        self.ani_system = ani_system
        self.camera = pygame.Rect(0, 0, RESOLUTION_X, RESOLUTION_Y)
        self.cache = cache
        self.target = target

        self.x = 0
        self.sprites = list()

        # load resources
        self.background = self.cache.get_image('background')
        self.tiles = self.cache.get_image('tiles')
        self.objects = self.cache.get_image('objects')

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the sprite who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.sprites if a.object_id == object_id][0]

    def move_camera(self, delta_x: int, delta_y: int) -> None:
        """Moves the camera rect by some pixels.
        """
        self.camera.x += delta_x
        self.camera.y += delta_y

    def world_to_screen_coord(self, x: float, y: float) -> pygame.math.Vector2:
        """Translates world coordinates into screen coordinates.
        In world coordinates, y leads from bottom to top (0,0 as bottom left).
        In screen coordinates, y leads from top to bottom (0,0 as top left).
        Returns a vector of integer coordinates.
        """
        x = int(x * WORLD_SCALE) - self.camera.x
        y = self.target.get_height() - (int(y * WORLD_SCALE) - self.camera.y)
        return pygame.math.Vector2(x, y)

    def screen_to_world_coord(self, x: int, y: int) -> pygame.math.Vector2:
        """Translates screen coordinates into world coordinates.
        Returns a vector of float coordinates.
        """
        x = self.camera.x + x / WORLD_SCALE
        y = self.camera.y + (self.target.get_height() - y) / WORLD_SCALE
        return pygame.math.Vector2(x, y)

    def draw_object(self, obj: physics.Object) -> None:
        """Draw an object.
        """
        objects = self.objects
        if obj.hsl is not None:
            objects = self.cache.get_hsl_transformed(objects, obj.hsl)

        # pos is bottom center, needs to be top left
        pos = self.world_to_screen_coord(obj.x, obj.y)
        pos.x -= OBJECT_SCALE // 2
        pos.y -= OBJECT_SCALE

        variation_col = 0
        clip = (variation_col * OBJECT_SCALE, obj.object_type * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE)
        self.target.blit(objects, (pos.x, pos.y), clip)

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

        # pos is bottom center, needs to be top left
        pos = self.world_to_screen_coord(phys_data.x, phys_data.y)
        pos.x -= SPRITE_SCALE // 2
        pos.y -= SPRITE_SCALE + ani_data.delta_y

        x_offset = (0 if phys_data.face_x >= 0.0 else 1) * ANIMATION_NUM_FRAMES * SPRITE_SCALE
        clip = pygame.Rect(ani_data.frame_id * SPRITE_SCALE + x_offset,
                           ani_data.action_id * SPRITE_SCALE, SPRITE_SCALE, SPRITE_SCALE)
        self.target.blit(sprite_sheet, (pos.x, pos.y), clip)

    def draw_ladder(self, ladder: physics.Ladder, tileset_col: int) -> None:
        """Draw a ladder.
        """
        tiles = self.tiles
        if ladder.hsl is not None:
            tiles = self.cache.get_hsl_transformed(tiles, ladder.hsl)

        # top left position
        pos = self.world_to_screen_coord(ladder.x, ladder.y)
        pos.y -= WORLD_SCALE

        # draw repeated ladder parts
        for i in range(ladder.height):
            self.target.blit(tiles, (pos.x, pos.y - i * WORLD_SCALE),
                             ((3 * tileset_col + 1) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE,
                              WORLD_SCALE, WORLD_SCALE * 2))

        # draw upper ladder part
        self.target.blit(tiles, (pos.x, pos.y - ladder.height * WORLD_SCALE),
                         ((3 * tileset_col) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE, WORLD_SCALE, WORLD_SCALE * 2))

        # draw lower ladder part
        self.target.blit(tiles, (pos.x, pos.y + WORLD_SCALE),
                         ((3 * tileset_col + 2) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE, WORLD_SCALE, WORLD_SCALE * 2))

    def draw_platform(self, platform: physics.Platform, tileset_col: int) -> None:
        """Draw a platform.
        """
        tiles = self.tiles
        if platform.hsl is not None:
            tiles = self.cache.get_hsl_transformed(tiles, platform.hsl)

        pos = self.world_to_screen_coord(platform.x, platform.y)

        for i in range(int(platform.width)):
            # draw texture below
            for j in range(int(platform.height)):
                self.target.blit(tiles,
                                 (pos.x + i * WORLD_SCALE, pos.y + j * WORLD_SCALE),
                                 ((3 * tileset_col+1) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE, WORLD_SCALE,
                                  WORLD_SCALE))

            # draw platform on top
            self.target.blit(tiles,
                             (pos.x + i * WORLD_SCALE, pos.y - WORLD_SCALE),
                             ((3 * tileset_col+1) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE, WORLD_SCALE,
                              WORLD_SCALE * 2))

        if platform.height > 0.0:
            # draw texture edges
            for j in range(int(platform.height)):
                self.target.blit(tiles,
                                 (pos.x - WORLD_SCALE, pos.y + j * WORLD_SCALE),
                                 (3 * tileset_col * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE, WORLD_SCALE, WORLD_SCALE))
                self.target.blit(tiles,
                                 (pos.x + int(platform.width) * WORLD_SCALE, pos.y + j * WORLD_SCALE),
                                 ((3 * tileset_col + 2) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE, WORLD_SCALE,
                                  WORLD_SCALE))

        # draw platform edges
        self.target.blit(tiles,
                         (pos.x - WORLD_SCALE, pos.y - WORLD_SCALE),
                         (3 * tileset_col * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE, WORLD_SCALE, WORLD_SCALE * 2))
        self.target.blit(tiles,
                         (pos.x + int(platform.width) * WORLD_SCALE, pos.y - WORLD_SCALE),
                         ((3 * tileset_col + 2) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE, WORLD_SCALE,
                          WORLD_SCALE * 2))

    def draw_projectile(self, proj: physics.Projectile) -> None:
        """Draw a projectile.
        """
        # pos is centered, but needs to be top left
        pos = self.world_to_screen_coord(proj.x, proj.y)
        pos.x -= OBJECT_SCALE // 2
        pos.y -= OBJECT_SCALE // 2

        variation_col = 0
        clip = pygame.Rect(variation_col * OBJECT_SCALE, proj.object_type * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE)

        angle = 2 * math.pi * proj.fly_ms / 360
        angle *= proj.spin_speed
        objects = self.cache.get_rotated_surface_clip(self.objects, clip, angle, flip=proj.face_x < 0.0)

        self.target.blit(objects, (pos.x, pos.y))

    def draw(self, bg_col: int) -> None:
        # background
        # FIXME: needs a better solution (also artistically) to work with the camera implementation
        # self.surface.blit(self.background, (0, 0), (bg_col * RESOLUTION_X, 0, RESOLUTION_X, RESOLUTION_Y))

        # foreground
        self.phys_system.platforms.sort(key=lambda plat: plat.y)

        # FIXME: needs a better spot
        tileset_col = 0

        for p in self.phys_system.platforms:
            self.draw_platform(p, tileset_col)

        for ladder in self.phys_system.ladders:
            self.draw_ladder(ladder, tileset_col)

        for o in self.phys_system.objects:
            self.draw_object(o)

        for s in self.sprites:
            self.draw_sprite(s)

        for proj in self.phys_system.projectiles:
            self.draw_projectile(proj)
