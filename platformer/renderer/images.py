import pygame
from typing import List
from dataclasses import dataclass
from enum import IntEnum

from core import constants, resources, objectids

from .. import animations, physics
from . import base, shapes


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
        self.actors = objectids.IdList()

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
    def get_platform_clip(tileset_col: int) -> Platform:
        left_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        left_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * constants.WORLD_SCALE,
                                  TileOffset.PLATFORM * constants.WORLD_SCALE)

        top_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        top_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * constants.WORLD_SCALE,
                                 TileOffset.PLATFORM * constants.WORLD_SCALE)

        right_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        right_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * constants.WORLD_SCALE,
                                   TileOffset.PLATFORM * constants.WORLD_SCALE)

        tex_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        tex_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * constants.WORLD_SCALE,
                                 TileOffset.TEXTURE * constants.WORLD_SCALE)

        return Platform(left_clip_rect=left_clip_rect, top_clip_rect=top_clip_rect, right_clip_rect=right_clip_rect,
                        tex_clip_rect=tex_clip_rect)

    @staticmethod
    def get_ladder_clip(tileset_col: int) -> Ladder:
        top_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        top_clip_rect.topleft = (NUM_FRAMES_PER_TILE * tileset_col * constants.WORLD_SCALE,
                                 TileOffset.LADDER * constants.WORLD_SCALE)

        mid_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        mid_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 1) * constants.WORLD_SCALE,
                                 TileOffset.LADDER * constants.WORLD_SCALE)

        bottom_clip_rect = pygame.Rect(0, 0, constants.WORLD_SCALE, constants.WORLD_SCALE)
        bottom_clip_rect.topleft = ((NUM_FRAMES_PER_TILE * tileset_col + 2) * constants.WORLD_SCALE,
                                    TileOffset.LADDER * constants.WORLD_SCALE)

        return Ladder(top_clip_rect=top_clip_rect, mid_clip_rect=mid_clip_rect, bottom_clip_rect=bottom_clip_rect)

    @staticmethod
    def get_object_clip(object_type: constants.ObjectType, variation_col: int) -> pygame.Rect:
        clip_rect = pygame.Rect(0, 0, constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        clip_rect.topleft = (variation_col * constants.OBJECT_SCALE, object_type * constants.OBJECT_SCALE)

        return clip_rect

    @staticmethod
    def get_actor_clip(face_x: physics.FaceDirection, frame_id: int, action: animations.Action) \
            -> pygame.Rect:
        x_offset = 0 if face_x == physics.FaceDirection.RIGHT else 1
        x_offset *= constants.ANIMATION_NUM_FRAMES * constants.SPRITE_SCALE

        clip_rect = pygame.Rect(0, 0, constants.SPRITE_SCALE, constants.SPRITE_SCALE)
        clip_rect.topleft = (frame_id * constants.SPRITE_SCALE + x_offset, action * constants.SPRITE_SCALE)

        return clip_rect

    @staticmethod
    def get_projectile_clip(object_type: constants.ObjectType, variation_col: int) -> pygame.Rect:
        clip_rect = pygame.Rect(0, 0, constants.OBJECT_SCALE, constants.OBJECT_SCALE)
        clip_rect.topleft = (variation_col * constants.OBJECT_SCALE, object_type * constants.OBJECT_SCALE)

        return clip_rect

    def draw_platform(self, platform: physics.Platform) -> None:
        pos = self.get_platform_rect(platform)
        pos.h *= -1
        clip = self.get_platform_clip(tileset_col=0)

        # draw textures
        pos_tmp = pos.copy()
        pos_tmp.y -= constants.WORLD_SCALE
        for y in range(platform.height):
            pos_tmp.x = pos.x
            for x in range(platform.width):
                self.target.blit(self.tiles, pos_tmp, clip.tex_clip_rect)
                pos_tmp.x += constants.WORLD_SCALE
            pos_tmp.y -= constants.WORLD_SCALE

        # draw platform
        pos_tmp = pos.copy()
        pos_tmp.y -= constants.WORLD_SCALE + platform.height * constants.WORLD_SCALE
        for x in range(platform.width):
            self.target.blit(self.tiles, pos_tmp, clip.top_clip_rect)
            pos_tmp.x += constants.WORLD_SCALE

        # draw edges
        self.target.blit(self.tiles, pos_tmp, clip.right_clip_rect)
        pos_tmp.x = pos.x - constants.WORLD_SCALE
        self.target.blit(self.tiles, pos_tmp, clip.left_clip_rect)

    def draw_ladder(self, ladder: physics.Ladder) -> None:
        pos = self.get_ladder_rect(ladder)
        clip = self.get_ladder_clip(tileset_col=0)

        # draw upper part of the ladder
        pos.y -= constants.WORLD_SCALE
        self.target.blit(self.tiles, pos, clip.top_clip_rect)
        pos.y += constants.WORLD_SCALE

        # draw ladder elements
        for i in range(ladder.height):
            self.target.blit(self.tiles, pos, clip.mid_clip_rect)
            pos.y += constants.WORLD_SCALE

        # draw lower part of the ladder:
        self.target.blit(self.tiles, pos, clip.bottom_clip_rect)

    def draw_object(self, obj: physics.Object) -> None:
        pos = self.get_object_rect(obj)
        clip = self.get_object_clip(object_type=obj.object_type, variation_col=0)
        self.target.blit(self.objects, pos, clip)

    def draw_actor(self, actor: physics.Actor) -> None:
        sprite_actor = self.sprite_context.actors.get_by_id(actor.object_id)
        ani_actor = self.ani_context.actors.get_by_id(actor.object_id)

        pos = self.get_actor_rect(actor)
        clip = self.get_actor_clip(face_x=actor.move.face_x, frame_id=ani_actor.frame.frame_id,
                                   action=ani_actor.frame.action)

        # apply movement offset from animation
        pos.y += ani_actor.oscillate.delta_y

        self.target.blit(sprite_actor.sprite_sheet, pos, clip)

    def draw_projectile(self, proj: physics.Projectile) -> None:
        # FIXME: allow for spinning animation
        """
        angle = 2 * math.pi * proj.fly_ms / 360
        angle *= proj.spin_speed
        objects = self.cache.get_rotated_surface_clip(self.objects, clip, angle, flip=proj.face_x < 0.0)
        """

        pos = self.get_projectile_rect(proj)
        clip = self.get_projectile_clip(object_type=proj.object_type, variation_col=0)
        self.target.blit(self.objects, pos, clip)

    def update(self, elapsed_ms: int) -> None:
        self.physics_context.platforms.sort(key=lambda plat: plat.pos.y)
