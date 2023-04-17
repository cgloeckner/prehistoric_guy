import unittest
import pygame

from core.constants import *

from platformer.renderer import camera
from platformer import physics
from platformer import animations


class CameraTest(unittest.TestCase):

    def setUp(self):
        surface = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))
        self.cam = camera.Camera(surface)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: regular coordinates
    def test__world_to_screen_coord__1(self):
        pos = self.cam.world_to_screen_coord(2.5, 3.5)
        self.assertEqual(pos.x, 2.5 * 32)
        self.assertEqual(pos.y, RESOLUTION_Y - 3.5 * 32)

    # Case 2: using camera
    def test__world_to_screen_coord__2(self):
        self.cam.move_ip(5, 3)
        pos = self.cam.world_to_screen_coord(2.5, 3.5)
        self.assertEqual(pos.x, 2.5 * 32 - 5)
        self.assertEqual(pos.y, RESOLUTION_Y - (3.5 * 32 - 3))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: regular coordinates
    def test__screen_to_world_coord__1(self):
        pos = self.cam.screen_to_world_coord(154, 97)
        self.assertAlmostEqual(pos.x, 154.0 / 32)
        self.assertAlmostEqual(pos.y, (RESOLUTION_Y - 97.0) / 32)

    # Case 2:
    def test__screen_to_world_coord__2(self):
        self.cam.move_ip(5, 3)
        pos = self.cam.screen_to_world_coord(154, 97)
        self.assertAlmostEqual(pos.x, (154 + 5) / 32)
        self.assertAlmostEqual(pos.y, (RESOLUTION_Y - 97.0 + 3) / 32)

    # ------------------------------------------------------------------------------------------------------------------

    def test__screen_to_world_inverts_world_to_screen(self):
        original = pygame.math.Vector2(154, 97)
        pos = self.cam.screen_to_world_coord(*original)
        got = self.cam.world_to_screen_coord(*pos)
        self.assertEqual(original.x, got.x)
        self.assertEqual(original.y, got.y)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_obj_rects(self):
        obj = physics.Object(pos=pygame.math.Vector2(2, 3), object_type=ObjectType.WEAPON)
        pos, clip = self.cam.get_object_rects(obj)

        screen_pos = self.cam.world_to_screen_coord(*obj.pos)

        self.assertEqual(pos.x, screen_pos.x - OBJECT_SCALE // 2)
        self.assertEqual(pos.y, screen_pos.y - OBJECT_SCALE)
        self.assertEqual(pos.width, OBJECT_SCALE)
        self.assertEqual(pos.height, OBJECT_SCALE)

        self.assertEqual(clip.x, 0 * OBJECT_SCALE)
        self.assertEqual(clip.y, ObjectType.WEAPON * OBJECT_SCALE)
        self.assertEqual(clip.width, OBJECT_SCALE)
        self.assertEqual(clip.height, OBJECT_SCALE)

    def test__get_actor_rects(self):
        actor = physics.Actor(object_id=1, pos=pygame.math.Vector2(2, 3), radius=5)
        ani = animations.Actor(object_id=1, frame_id=7, action=animations.Action.THROW)

        screen_pos = self.cam.world_to_screen_coord(*actor.pos)

        pos, clip = self.cam.get_actor_rects(actor, ani)

        self.assertEqual(pos.x, screen_pos.x - SPRITE_SCALE // 2)
        self.assertEqual(pos.y, screen_pos.y - SPRITE_SCALE)
        self.assertEqual(pos.width, SPRITE_SCALE)
        self.assertEqual(pos.height, SPRITE_SCALE)

        self.assertEqual(clip.x, 7 * SPRITE_SCALE)
        self.assertEqual(clip.y, animations.Action.THROW * SPRITE_SCALE)
        self.assertEqual(clip.width, SPRITE_SCALE)
        self.assertEqual(clip.height, SPRITE_SCALE)

    def test__get_ladder_rect(self):
        ladder = physics.Ladder(pos=pygame.math.Vector2(3, 2), height=5)

        screen_pos = self.cam.world_to_screen_coord(*ladder.pos)

        pos, top, mid, bottom = self.cam.get_ladder_rects(ladder, 11)

        self.assertEqual(pos.x, screen_pos.x - WORLD_SCALE // 2)
        self.assertEqual(pos.y, screen_pos.y - 5 * WORLD_SCALE)
        self.assertEqual(pos.width, WORLD_SCALE)
        self.assertEqual(pos.height, 5 * WORLD_SCALE)

        self.assertEqual(top.x, camera.NUM_FRAMES_PER_TILE * 11 * WORLD_SCALE)
        self.assertEqual(top.y, camera.LADDER_ROW * WORLD_SCALE)
        self.assertEqual(top.width, WORLD_SCALE)
        self.assertEqual(top.height, WORLD_SCALE)

        self.assertEqual(mid.x, (camera.NUM_FRAMES_PER_TILE * 11 + 1) * WORLD_SCALE)
        self.assertEqual(mid.y, camera.LADDER_ROW * WORLD_SCALE)
        self.assertEqual(mid.width, WORLD_SCALE)
        self.assertEqual(mid.height, WORLD_SCALE)

        self.assertEqual(bottom.x, (camera.NUM_FRAMES_PER_TILE * 11 + 2) * WORLD_SCALE)
        self.assertEqual(bottom.y, camera.LADDER_ROW * WORLD_SCALE)
        self.assertEqual(bottom.width, WORLD_SCALE)
        self.assertEqual(bottom.height, WORLD_SCALE)

    def test__get_platform_rect(self):
        platform = physics.Platform(pos=pygame.math.Vector2(1, 2), width=5, height=3)

        screen_pos = self.cam.world_to_screen_coord(*platform.pos)

        pos, left, plat, right, tex = self.cam.get_platform_rects(platform, 7)

        self.assertEqual(pos.x, screen_pos.x)
        self.assertEqual(pos.y, screen_pos.y)
        self.assertEqual(pos.width, 5 * WORLD_SCALE)
        self.assertEqual(pos.height, 3 * WORLD_SCALE)

        self.assertEqual(left.x, camera.NUM_FRAMES_PER_TILE * 7 * WORLD_SCALE)
        self.assertEqual(left.y, camera.PLATFORM_ROW * WORLD_SCALE)
        self.assertEqual(left.width, WORLD_SCALE)
        self.assertEqual(left.height, WORLD_SCALE)

        self.assertEqual(plat.x, (camera.NUM_FRAMES_PER_TILE * 7 + 1) * WORLD_SCALE)
        self.assertEqual(plat.y, camera.PLATFORM_ROW * WORLD_SCALE)
        self.assertEqual(plat.width, WORLD_SCALE)
        self.assertEqual(plat.height, WORLD_SCALE)

        self.assertEqual(right.x, (camera.NUM_FRAMES_PER_TILE * 7 + 2) * WORLD_SCALE)
        self.assertEqual(right.y, camera.PLATFORM_ROW * WORLD_SCALE)
        self.assertEqual(right.width, WORLD_SCALE)
        self.assertEqual(right.height, WORLD_SCALE)

        self.assertEqual(tex.x, (camera.NUM_FRAMES_PER_TILE * 7 + 1) * WORLD_SCALE)
        self.assertEqual(tex.y, camera.TEXTURE_ROW * WORLD_SCALE)
        self.assertEqual(tex.width, WORLD_SCALE)
        self.assertEqual(tex.height, WORLD_SCALE)

    def test__get_projectile_rects(self):
        proj = physics.Projectile(object_id=10, pos=pygame.math.Vector2(2, 3), radius=0.5, object_type=ObjectType.DANGER)
        pos, clip = self.cam.get_projectile_rects(proj)

        screen_pos = self.cam.world_to_screen_coord(*proj.pos)

        self.assertEqual(pos.x, screen_pos.x - OBJECT_SCALE // 2)
        self.assertEqual(pos.y, screen_pos.y - OBJECT_SCALE // 2)
        self.assertEqual(pos.width, OBJECT_SCALE)
        self.assertEqual(pos.height, OBJECT_SCALE)

        self.assertEqual(clip.x, 0 * OBJECT_SCALE)
        self.assertEqual(clip.y, ObjectType.DANGER * OBJECT_SCALE)
        self.assertEqual(clip.width, OBJECT_SCALE)
        self.assertEqual(clip.height, OBJECT_SCALE)
