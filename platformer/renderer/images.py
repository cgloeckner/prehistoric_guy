import pygame
from typing import List
from dataclasses import dataclass

from core.constants import *
from core import resources

from platformer.renderer import base
from platformer.renderer import shapes
from platformer import animations
from platformer import physics


NUM_FRAMES_PER_TILE: int = 3


class TileOffset(IntEnum):
    PLATFORM = 0
    TEXTURE = 2
    LADDER = 3


@dataclass
class Platform:
    left_clip_rect: pygame.Rect
    right_clip_rect: pygame.Rect
    top_clip_rect: pygame.Rect
    tex_clip_rect: pygame.Rect


@dataclass
class Ladder:
    top_clip_rect: pygame.Rect
    mid_clip_rect: pygame.Rect
    bottom_clip_rect: pygame.Rect


@dataclass
class Actor:
    object_id: int
    sprite_sheet: pygame.Surface


class Context:
    def __init__(self):
        self.actors: List[Actor] = list()

    def get_actor_by_id(self, object_id: int) -> Actor:
        for actor in self.actors:
            if actor.object_id == object_id:
                return actor

        # FIXME
        raise ValueError(f'No such Actor {object_id}')

    def create_actor(self, object_id: int, sprite_sheet: pygame.Surface) -> Actor:
        a = Actor(object_id=object_id, sprite_sheet=sprite_sheet)
        self.actors.append(a)
        return a


# ----------------------------------------------------------------------------------------------------------------------


class ImageRenderer(shapes.ShapeRenderer):
    def __init__(self, camera: base.Camera, target: pygame.Surface, physics_context: physics.Context,
                 ani_context: animations.Context, sprite_context: Context, cache: resources.Cache):
        super().__init__(camera, target, physics_context)
        self.ani_context = ani_context
        self.sprite_context = sprite_context
        self.cache = cache

        # resources
        self.tiles = self.cache.get_image('tiles')
        self.objects = self.cache.get_image('objects')

    @staticmethod
    def get_platform_clip(scale: int, tileset_col: int) -> Platform:
        left_clip_rect = pygame.Rect(0, 0, scale, scale)
        left_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * scale, TileOffset.PLATFORM * scale)

        top_clip_rect = pygame.Rect(0, 0, scale, scale)
        top_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * scale, TileOffset.PLATFORM * scale)

        right_clip_rect = pygame.Rect(0, 0, scale, scale)
        right_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * scale, TileOffset.PLATFORM * scale)

        tex_clip_rect = pygame.Rect(0, 0, scale, scale)
        tex_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * scale, TileOffset.TEXTURE * scale)

        return Platform(left_clip_rect=left_clip_rect, top_clip_rect=top_clip_rect, right_clip_rect=right_clip_rect,
                        tex_clip_rect=tex_clip_rect)

    @staticmethod
    def get_ladder_clip(scale: int, tileset_col: int) -> Ladder:
        top_clip_rect = pygame.Rect(0, 0, scale, scale)
        top_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * scale, TileOffset.LADDER * scale)

        mid_clip_rect = pygame.Rect(0, 0, scale, scale)
        mid_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * scale, TileOffset.LADDER * scale)

        bottom_clip_rect = pygame.Rect(0, 0, scale, scale)
        bottom_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * scale, TileOffset.LADDER * scale)

        return Ladder(top_clip_rect=top_clip_rect, mid_clip_rect=mid_clip_rect, bottom_clip_rect=bottom_clip_rect)

    @staticmethod
    def get_object_clip(scale: int, object_type: physics.ObjectType, variation_col: int) -> pygame.Rect:
        clip_rect = pygame.Rect(0, 0, scale, scale)
        clip_rect.topleft = (variation_col * scale, object_type * scale)

        return clip_rect

    @staticmethod
    def get_actor_clip(scale: int, frame_id: int, action: animations.Action, face_x: physics.FaceDirection) \
            -> pygame.Rect:
        x_offset = 0 if face_x == physics.FaceDirection.RIGHT else 1
        x_offset *= ANIMATION_NUM_FRAMES * scale

        clip_rect = pygame.Rect(0, 0, scale, scale)
        clip_rect.topleft = (frame_id * scale + x_offset, action * scale)

        return clip_rect

    @staticmethod
    def get_projectile_clip(scale: int, object_type: physics.ObjectType, variation_col: int) -> pygame.Rect:
        clip_rect = pygame.Rect(0, 0, scale, scale)
        clip_rect.topleft = (variation_col * scale, object_type * scale)

        return clip_rect

    def draw_platform(self, platform: physics.Platform) -> None:
        pos = self.get_platform_rect(platform)
        pos.h *= -1
        clip = self.get_platform_clip(WORLD_SCALE, 0)

        # draw textures
        pos_tmp = pos.copy()
        pos_tmp.y -= WORLD_SCALE
        for y in range(platform.height):
            pos_tmp.x = pos.x
            for x in range(platform.width):
                self.target.blit(self.tiles, pos_tmp, clip.tex_clip_rect)
                pos_tmp.x += WORLD_SCALE
            pos_tmp.y -= WORLD_SCALE

        # draw platform
        pos_tmp = pos.copy()
        pos_tmp.y -= WORLD_SCALE + platform.height * WORLD_SCALE
        for x in range(platform.width):
            self.target.blit(self.tiles, pos_tmp, clip.top_clip_rect)
            pos_tmp.x += WORLD_SCALE

        # draw edges
        self.target.blit(self.tiles, pos_tmp, clip.right_clip_rect)
        pos_tmp.x = pos.x - WORLD_SCALE
        self.target.blit(self.tiles, pos_tmp, clip.left_clip_rect)

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        pos = self.get_ladder_rect(ladder)
        clip = self.get_ladder_clip(WORLD_SCALE, 0)

        # draw upper part of the ladder
        pos.y -= WORLD_SCALE
        self.target.blit(self.tiles, pos, clip.top_clip_rect)
        pos.y += WORLD_SCALE

        # draw ladder elements
        for i in range(ladder.height):
            self.target.blit(self.tiles, pos, clip.mid_clip_rect)
            pos.y += WORLD_SCALE

        # draw lower part of the ladder:
        self.target.blit(self.tiles, pos, clip.bottom_clip_rect)

    def draw_object(self, obj: physics.Object) -> None:
        pos = self.get_object_rect(obj)
        clip = self.get_object_clip(OBJECT_SCALE, obj.object_type, 0)
        self.target.blit(self.objects, pos, clip)

    def draw_actor(self, actor: physics.Actor) -> None:
        sprite_actor = self.sprite_context.get_actor_by_id(actor.object_id)
        ani_actor = self.ani_context.get_actor_by_id(actor.object_id)

        pos = self.get_actor_rect(actor)
        clip = self.get_actor_clip(SPRITE_SCALE, ani_actor.frame_id, ani_actor.action, face_x=actor.movement.face_x)

        # apply movement offset from animation
        pos.y += ani_actor.delta_y

        self.target.blit(sprite_actor.sprite_sheet, pos, clip)

    def draw_projectile(self, proj: physics.Projectile) -> None:
        # FIXME: allow for spinning animation
        """
        angle = 2 * math.pi * proj.fly_ms / 360
        angle *= proj.spin_speed
        objects = self.cache.get_rotated_surface_clip(self.objects, clip, angle, flip=proj.face_x < 0.0)
        """

        pos = self.get_projectile_rect(proj)
        clip = self.get_projectile_clip(SPRITE_SCALE, proj.object_type, 0)
        self.target.blit(self.objects, pos, clip)

    def update(self, elapsed_ms: int) -> None:
        self.physics_context.platforms.sort(key=lambda plat: plat.pos.y)


if __name__ == '__main__':
    phy_ctx = physics.Context()
    phy_ctx.create_platform(x=1, y=0, width=3, height=2)
    phy_ctx.create_platform(x=8, y=3, width=4)
    phy_ctx.create_platform(x=7, y=5, width=2)
    phy_ctx.create_platform(x=1, y=5, width=3)
    phy_ctx.create_ladder(x=9, y=3, height=2)
    phy_ctx.create_object(x=1.5, y=3, object_type=physics.ObjectType.FOOD)
    phy_ctx.create_actor(1, x=8.5, y=5)
    phy_ctx.create_projectile(2, x=6.5, y=5.5)

    ani_ctx = animations.Context()
    ani_ctx.create_actor(1)

    sprite_ctx = Context()

    cam = base.Camera(10 * WORLD_SCALE, 6 * WORLD_SCALE)
    #cam.center.x += -0.5

    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    buffer = pygame.Surface((cam.width, cam.height))

    img_cache = resources.Cache('../../data')
    sprite_ctx.create_actor(1, img_cache.get_image('guy'))

    r = ImageRenderer(cam, buffer, phy_ctx, ani_ctx, sprite_ctx, img_cache)
    r.draw()

    pygame.image.save(buffer, '/tmp/test.png')
