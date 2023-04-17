import unittest
import os
import pygame

from core import constants, resources

from platformer import physics, animations
from platformer.renderer import base, images


class ImageRendererTest(unittest.TestCase):

    def setUp(self):
        self.phy_ctx = physics.Context()
        self.phy_ctx.create_platform(x=1, y=0, width=3, height=2)
        self.phy_ctx.create_platform(x=8, y=3, width=4)
        self.phy_ctx.create_platform(x=7, y=5, width=2)
        self.phy_ctx.create_platform(x=1, y=5, width=3)
        self.phy_ctx.create_ladder(x=9, y=3, height=2)
        self.phy_ctx.create_object(x=1.5, y=3, object_type=physics.ObjectType.FOOD)
        self.phy_ctx.create_actor(1, x=8.5, y=5)
        self.phy_ctx.create_projectile(2, x=6.5, y=5.5)

        self.ani_ctx = animations.Context()
        self.ani_ctx.create_actor(1)

        self.sprite_ctx = images.Context()

        self.cam = base.Camera(320, 192)
        self.cam.center.x = -1.5
        self.cam.center.y = -0.5

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.buffer = pygame.Surface((self.cam.width, self.cam.height))

        # create empty dummy surfaces of the correct sizes
        self.cache = resources.Cache()
        guy_path = self.cache.get_image_filename('guy')
        self.cache.images[str(guy_path)] = pygame.Surface((constants.ANIMATION_NUM_FRAMES * constants.SPRITE_SCALE,
                                                           len(animations.Action) * constants.SPRITE_SCALE))
        obj_path = self.cache.get_image_filename('object')
        self.cache.images[str(obj_path)] = pygame.Surface((constants.OBJECT_NUM_VERSIONS * constants.OBJECT_SCALE,
                                                           len(constants.ObjectType) * constants.OBJECT_SCALE))
        tile_path = self.cache.get_image_filename('tiles')
        self.cache.images[str(tile_path)] = pygame.Surface((images.NUM_FRAMES_PER_TILE * constants.WORLD_SCALE,
                                                            len(images.TileOffset) * 3 * constants.WORLD_SCALE))

        self.sprite_ctx.create_actor(1, self.cache.get_image('guy'))

        self.renderer = images.ImageRenderer(self.cam, self.buffer, self.phy_ctx, self.ani_ctx, self.sprite_ctx,
                                             self.cache)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_platform_rect(self):
        clip = self.renderer.get_platform_clip(tileset_col=2)

        self.assertEqual(clip.left_clip_rect.x, images.NUM_FRAMES_PER_TILE * 2 * constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.y, images.TileOffset.PLATFORM * constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.top_clip_rect.x, (images.NUM_FRAMES_PER_TILE * 2 + 1) * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.y, images.TileOffset.PLATFORM * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.right_clip_rect.x, (images.NUM_FRAMES_PER_TILE * 2 + 2) * constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.y, images.TileOffset.PLATFORM * constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.tex_clip_rect.x, (images.NUM_FRAMES_PER_TILE * 2 + 1) * constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.y, images.TileOffset.TEXTURE * constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.height, constants.WORLD_SCALE)

    def test__get_ladder_rect(self):
        clip = self.renderer.get_ladder_clip(tileset_col=2)

        self.assertEqual(clip.top_clip_rect.x, images.NUM_FRAMES_PER_TILE * 2 * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.y, images.TileOffset.LADDER * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.mid_clip_rect.x, (images.NUM_FRAMES_PER_TILE * 2 + 1) * constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.y, images.TileOffset.LADDER * constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.bottom_clip_rect.x, (images.NUM_FRAMES_PER_TILE * 2 + 2) * constants.WORLD_SCALE)
        self.assertEqual(clip.bottom_clip_rect.y, images.TileOffset.LADDER * constants.WORLD_SCALE)
        self.assertEqual(clip.bottom_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.bottom_clip_rect.height, constants.WORLD_SCALE)

    def test__get_object_rect(self):
        obj = self.phy_ctx.objects[0]
        clip = self.renderer.get_object_clip(object_type=obj.object_type, variation_col=1)

        self.assertEqual(clip.x, 1 * constants.OBJECT_SCALE)
        self.assertEqual(clip.y, obj.object_type * constants.OBJECT_SCALE)
        self.assertEqual(clip.width, constants.OBJECT_SCALE)
        self.assertEqual(clip.height, constants.OBJECT_SCALE)

    def test__get_actor_rect(self):
        phy_actor = self.phy_ctx.actors[0]
        ani_actor = self.ani_ctx.actors[0]
        ani_actor.frame_id = 7
        ani_actor.action = animations.Action.THROW
        clip = self.renderer.get_actor_clip(face_x=phy_actor.movement.face_x, frame_id=ani_actor.frame_id,
                                            action=ani_actor.action)

        self.assertEqual(clip.x, 7 * constants.SPRITE_SCALE)
        self.assertEqual(clip.y, animations.Action.THROW * constants.SPRITE_SCALE)
        self.assertEqual(clip.width, constants.SPRITE_SCALE)
        self.assertEqual(clip.height, constants.SPRITE_SCALE)

    def test__get_projectile_rects(self):
        proj = self.phy_ctx.projectiles[0]
        clip = self.renderer.get_projectile_clip(object_type=proj.object_type, variation_col=2)

        self.assertEqual(clip.x, 2 * constants.OBJECT_SCALE)
        self.assertEqual(clip.y, proj.object_type * constants.OBJECT_SCALE)
        self.assertEqual(clip.width, constants.OBJECT_SCALE)
        self.assertEqual(clip.height, constants.OBJECT_SCALE)

    # ------------------------------------------------------------------------------------------------------------------

    def test_draw_does_not_raise(self):
        self.renderer.draw()
