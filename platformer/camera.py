import pygame
from typing import Tuple, List

from core.constants import *

from platformer import physics
from platformer import animations


NUM_FRAMES_PER_TILE: int = 3

# tiles row offsets
PLATFORM_ROW: int = 0
TEXTURE_ROW: int = 2
LADDER_ROW: int = 3


class Camera(pygame.Rect):
    def __init__(self, target: pygame.Surface):
        super().__init__(0, 0, RESOLUTION_X, RESOLUTION_Y)
        self.target = target
        # FIXME: use buffer later to zoom
        self.buffer = pygame.Surface(target.get_size())
        self.buffer.fill('black')

        self.follow: List[physics.Actor] = list()

    def update(self, elapsed_ms: int) -> None:
        if len(self.follow) == 0:
            return

        # calculate center of all given actors
        pos = pygame.math.Vector2()
        for actor in self.follow:
            pos.x += actor.x
            pos.y += actor.y
        pos /= len(self.follow)
        self.center = pos * WORLD_SCALE

    def world_to_screen_coord(self, x: float, y: float) -> pygame.math.Vector2:
        """Translates world coordinates into screen coordinates.
        In world coordinates, y leads from bottom to top (0,0 as bottom left).
        In screen coordinates, y leads from top to bottom (0,0 as top left).
        Returns a vector of integer coordinates.
        """
        x = int(x * WORLD_SCALE) - self.x
        y = self.target.get_height() - (int(y * WORLD_SCALE) - self.y)
        return pygame.math.Vector2(x, y)

    def screen_to_world_coord(self, x: int, y: int) -> pygame.math.Vector2:
        """Translates screen coordinates into world coordinates.
        Returns a vector of float coordinates.
        """
        x = self.x + x / WORLD_SCALE
        y = self.y + (self.target.get_height() - y) / WORLD_SCALE
        return pygame.math.Vector2(x, y)

    def get_object_rects(self, obj: physics.Object) -> Tuple[pygame.Rect, pygame.Rect]:
        """Returns the positioning and clipping rectangles.
        """
        # FIXME: make more flexible
        variation_col = 0

        pos_rect = pygame.Rect(0, 0, OBJECT_SCALE, OBJECT_SCALE)
        pos_rect.midbottom = self.world_to_screen_coord(obj.x, obj.y)

        clip_rect = pygame.Rect(0, 0, OBJECT_SCALE, OBJECT_SCALE)
        clip_rect.topleft = (variation_col * OBJECT_SCALE, obj.object_type * OBJECT_SCALE)

        return pos_rect, clip_rect

    def get_actor_pos(self, actor: physics.Actor) -> pygame.Rect:
        """Returns the positioning rectangles. This is separated, because the clipping rectangle also requires the
        actor's animation data.
        """
        pos_rect = pygame.Rect(0, 0, SPRITE_SCALE, SPRITE_SCALE)
        pos_rect.midbottom = self.world_to_screen_coord(actor.x, actor.y)

        return pos_rect

    def get_actor_rects(self, actor: physics.Actor, ani: animations.Actor) -> Tuple[pygame.Rect, pygame.Rect]:
        """Returns the positioning and clipping rectangles.
        """
        pos_rect = self.get_actor_pos(actor)

        clip_rect = pygame.Rect(0, 0, SPRITE_SCALE, SPRITE_SCALE)
        x_offset = 0 if actor.face_x >= 0.0 else 1
        x_offset *= ANIMATION_NUM_FRAMES * SPRITE_SCALE
        clip_rect.topleft = (ani.frame_id * SPRITE_SCALE + x_offset, ani.action_id * SPRITE_SCALE)

        return pos_rect, clip_rect

    def get_ladder_rects(self, ladder: physics.Ladder, tileset_col: int = 0)\
            -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
        """Returns the positioning rect and three clipping rectangles: 1st for the top, 2nd for the
        middle and 3rd for the bottom of the ladder.
        """
        pos_rect = pygame.Rect(0, 0, WORLD_SCALE, ladder.height * WORLD_SCALE)
        pos_rect.midbottom = self.world_to_screen_coord(ladder.x, ladder.y)

        top_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        top_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * WORLD_SCALE, LADDER_ROW * WORLD_SCALE)

        mid_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        mid_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE)

        bottom_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        bottom_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * WORLD_SCALE, LADDER_ROW * WORLD_SCALE)

        return pos_rect, top_clip_rect, mid_clip_rect, bottom_clip_rect

    def get_platform_rects(self, platform: physics.Platform, tileset_col: int = 0) \
            -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
        """Returns the positioning rect and four clipping rectangle: 1st for the left edge, 2nd for the middle platform,
        3rd for right edge and 4th for the texture below.
        """
        pos_rect = pygame.Rect(0, 0, platform.width * WORLD_SCALE, platform.height * WORLD_SCALE)
        pos_rect.topleft = self.world_to_screen_coord(platform.x, platform.y)

        left_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        left_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE)

        mid_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        mid_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE)

        right_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        right_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * WORLD_SCALE, PLATFORM_ROW * WORLD_SCALE)

        tex_clip_rect = pygame.Rect(0, 0, WORLD_SCALE, WORLD_SCALE)
        tex_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * WORLD_SCALE, TEXTURE_ROW * WORLD_SCALE)

        return pos_rect, left_clip_rect, mid_clip_rect, right_clip_rect, tex_clip_rect

    def get_projectile_rects(self, proj: physics.Projectile) -> Tuple[pygame.Rect, pygame.Rect]:
        """Returns the positioning and clipping rectangles.
        """
        # FIXME: make more flexible
        variation_col = 0

        pos_rect = pygame.Rect(0, 0, OBJECT_SCALE, OBJECT_SCALE)
        pos_rect.center = self.world_to_screen_coord(proj.x, proj.y)

        clip_rect = pygame.Rect(0, 0, OBJECT_SCALE, OBJECT_SCALE)
        clip_rect.topleft = (variation_col * OBJECT_SCALE, proj.object_type * OBJECT_SCALE)

        return pos_rect, clip_rect

    def draw(self) -> None:
        # FIXME: use buffer to zoom
        self.target.blit(self.buffer, (0, 0))
        self.buffer.fill('black')
