import tempfile
import unittest
import os
import pygame
import pathlib

from core import constants, resources, paths

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
        self.phy_ctx.create_object(x=1.5, y=3, object_type=constants.ObjectType.FOOD)
        self.phy_ctx.create_actor(1, x=8.5, y=5)
        self.phy_ctx.create_projectile(2, x=6.5, y=5.5)

        self.ani_ctx = animations.Context()
        self.ani_ctx.create_actor(1)

        self.sprite_ctx = images.Context()

        self.cam = base.Camera((320, 192))
        self.cam.topleft.x = -1.5
        self.cam.topleft.y = -0.5

        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        self.buffer = pygame.Surface((self.cam.width, self.cam.height))

        self.tempdir = tempfile.TemporaryDirectory()
        root = pathlib.Path(self.tempdir.name)

        # create empty dummy surfaces of the correct sizes
        data_paths = paths.DataPath(root)
        self.cache = resources.Cache(data_paths)
        guy_path = data_paths.sprite('guy')
        guy_path.touch()
        self.cache.images[str(guy_path)] = pygame.Surface((constants.ANIMATION_NUM_FRAMES * constants.SPRITE_SCALE,
                                                           len(animations.Action) * constants.SPRITE_SCALE))
        obj_path = data_paths('objects', 'png')
        obj_path.touch()
        self.cache.images[str(obj_path)] = pygame.Surface((constants.OBJECT_NUM_VERSIONS * constants.OBJECT_SCALE,
                                                           len(constants.ObjectType) * constants.OBJECT_SCALE))
        tile_path = data_paths.tile('grass')
        tile_path.touch()
        self.cache.images[str(tile_path)] = pygame.Surface((0, 6 * constants.WORLD_SCALE))

        self.sprite_ctx.create_actor(1, self.cache.get_image(guy_path))

        self.renderer = images.ImageRenderer(self.cam, self.buffer, self.phy_ctx, self.ani_ctx, self.sprite_ctx,
                                             self.cache)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_platform_rect(self):
        clip = self.renderer.get_platform_clip()

        self.assertEqual(clip.left_clip_rect.x, 0)
        self.assertEqual(clip.left_clip_rect.y, 0)
        self.assertEqual(clip.left_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.top_clip_rect.x, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.y, 0)
        self.assertEqual(clip.top_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.right_clip_rect.x, 2 * constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.y, 0)
        self.assertEqual(clip.right_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.tex_clip_rect.x, constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.y, constants.WORLD_SCALE * 2)
        self.assertEqual(clip.tex_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.height, constants.WORLD_SCALE)

        clip = self.renderer.get_platform_clip(alt_platform=True)

        self.assertEqual(clip.left_clip_rect.x, 3 * constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.y, 0)
        self.assertEqual(clip.left_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.left_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.top_clip_rect.x, 4 * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.y, 0)
        self.assertEqual(clip.top_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.right_clip_rect.x, 5 * constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.y, 0)
        self.assertEqual(clip.right_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.right_clip_rect.height, constants.WORLD_SCALE * 2)

        self.assertEqual(clip.tex_clip_rect.x, constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.y, constants.WORLD_SCALE * 2)
        self.assertEqual(clip.tex_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.tex_clip_rect.height, constants.WORLD_SCALE)

    def test__get_ladder_rect(self):
        clip = self.renderer.get_ladder_clip()

        self.assertEqual(clip.top_clip_rect.x, 3 * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.y, 2 * constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.top_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.mid_clip_rect.x, 4 * constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.y, 2 * constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.width, constants.WORLD_SCALE)
        self.assertEqual(clip.mid_clip_rect.height, constants.WORLD_SCALE)

        self.assertEqual(clip.bottom_clip_rect.x, 5 * constants.WORLD_SCALE)
        self.assertEqual(clip.bottom_clip_rect.y, 2 * constants.WORLD_SCALE)
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
        clip = self.renderer.get_actor_clip(face_x=phy_actor.move.face_x, frame_id=ani_actor.frame_id,
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
