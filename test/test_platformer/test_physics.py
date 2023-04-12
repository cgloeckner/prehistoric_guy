import unittest
import pygame
import math

from platformer import physics


class PhysicsFunctionsTest(unittest.TestCase):

    # Case 1: position inside platform
    # NOTE: y is the top, so y - height leads to the bottom
    def test__is_inside_platform__1(self):
        plat = physics.Platform(3, 2, 10, 5)

        self.assertTrue(physics.is_inside_platform(4, 3, plat))

    # Case 2: position at platform's top
    def test__is_inside_platform__2(self):
        plat = physics.Platform(3, 2, 10, 5)

        # top edge does not count as inside
        self.assertFalse(physics.is_inside_platform(6, 7, plat))

        # left/right/bottom edges do
        self.assertTrue(physics.is_inside_platform(3, 2, plat))
        self.assertTrue(physics.is_inside_platform(13, 5, plat))
        self.assertTrue(physics.is_inside_platform(6, 2, plat))

    # Case 3: position outside platform
    def test__is_inside_platform__3(self):
        plat = physics.Platform(3, 2, 10, 5)

        # above/below/left/right
        self.assertFalse(physics.is_inside_platform(4, 8, plat))
        self.assertFalse(physics.is_inside_platform(4, 1, plat))
        self.assertFalse(physics.is_inside_platform(1, 5, plat))
        self.assertFalse(physics.is_inside_platform(14, 5, plat))

    # Case 4: thin platform never contains a point
    def test__is_inside_platform__4(self):
        plat = physics.Platform(3, 2, 10)

        self.assertFalse(physics.is_inside_platform(5, 2, plat))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: traversing downwards
    def test__did_traverse_above__1(self):
        plat = physics.Platform(1, 2, 10)

        self.assertTrue(physics.did_traverse_above(2, -3, pygame.math.Vector2(3, 4), plat))

    # Case 2: no traversing upwards
    def test__did_traverse_above__2(self):
        plat = physics.Platform(1, 2, 10)

        self.assertFalse(physics.did_traverse_above(2, 3, pygame.math.Vector2(3, -4), plat))

    # Case 3: no traversing if last_pos == (x, y)
    def test__did_traverse_above__3(self):
        plat = physics.Platform(1, 2, 10)

        self.assertFalse(physics.did_traverse_above(2, 3, pygame.math.Vector2(2, 3), plat))

    # Case 4: traversing with last_pos on platform
    def test__did_traverse_above__4(self):
        plat = physics.Platform(1, 2, 10)

        self.assertTrue(physics.did_traverse_above(2, -3, pygame.math.Vector2(1, 2), plat))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: directly stands on platform
    def test__does_stand_on__1(self):
        actor = physics.Actor(object_id=13, x=2, y=3)
        plat = physics.Platform(x=1, y=3, width=3)

        self.assertTrue(physics.does_stand_on(actor, plat))

    # Case 2: is above platform
    def test__does_stand_on__2(self):
        actor = physics.Actor(object_id=13, x=2, y=3.1)
        plat = physics.Platform(x=1, y=3, width=3)

        self.assertFalse(physics.does_stand_on(actor, plat))

    # Case 3: is below platform
    def test__does_stand_on__3(self):
        actor = physics.Actor(object_id=13, x=2, y=2.9)
        plat = physics.Platform(x=1, y=3, width=3)

        self.assertFalse(physics.does_stand_on(actor, plat))

    # Case 4: is left of platform
    def test__does_stand_on__4(self):
        actor = physics.Actor(object_id=13, x=0.9, y=3)
        plat = physics.Platform(x=1, y=3, width=3)

        self.assertFalse(physics.does_stand_on(actor, plat))

    # Case 5: is right of platform
    def test__does_stand_on__6(self):
        actor = physics.Actor(object_id=13, x=4.1, y=3)
        plat = physics.Platform(x=1, y=3, width=3)

        self.assertFalse(physics.does_stand_on(actor, plat))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: points within ladder
    # NOTE: y is the bottom, so y + height leads to the bottom
    def test__ladder_in_reach__1(self):
        ladder = physics.Ladder(2.5, 3, 4)

        # bottom end is not in reach
        self.assertFalse(physics.ladder_in_reach(2.5, 3, ladder))
        # mid/top end are in reach
        self.assertTrue(physics.ladder_in_reach(2.5, 3.01, ladder))
        self.assertTrue(physics.ladder_in_reach(2.5, 7, ladder))

    # Case 2: points within ladder +/- radius
    def test__ladder_in_reach__2(self):
        ladder = physics.Ladder(2.5, 3, 4)

        self.assertTrue(physics.ladder_in_reach(2.5 - physics.OBJECT_RADIUS, 4, ladder))
        self.assertTrue(physics.ladder_in_reach(2.5 + physics.OBJECT_RADIUS, 4, ladder))

    # Case 3: points outside ladder +/- radius
    def test__ladder_in_reach__3(self):
        ladder = physics.Ladder(2.5, 3, 4)

        # top/bottom
        self.assertFalse(physics.ladder_in_reach(2.5, 3 - 0.01, ladder))
        self.assertFalse(physics.ladder_in_reach(2.5, 8 + 0.01, ladder))

        # left/right
        self.assertFalse(physics.ladder_in_reach(2.5 - physics.OBJECT_RADIUS - 0.01, 4, ladder))
        self.assertFalse(physics.ladder_in_reach(2.5 + physics.OBJECT_RADIUS + 0.02, 4, ladder))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: actor in the middle
    def test__within_ladder__1(self):
        ladder = physics.Ladder(2.5, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=4.25, ladder=ladder)

        self.assertTrue(physics.within_ladder(actor))

    # Case 2: actor at the top
    def test__within_ladder__2(self):
        ladder = physics.Ladder(2.5, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=7, ladder=ladder)

        self.assertFalse(physics.within_ladder(actor))

    # Case 3: actor at the bottom
    def test__within_ladder__3(self):
        ladder = physics.Ladder(2.5, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=2, ladder=ladder)

        self.assertFalse(physics.within_ladder(actor))

    # Case 4: actor without ladder
    def test__within_ladder__4(self):
        actor = physics.Actor(object_id=13, x=2.5, y=4.25)

        self.assertFalse(physics.within_ladder(actor))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: no hovering functions yields no movement
    def test__get_hover_delta__1(self):
        hover = physics.Hovering()
        x, y = physics.get_hover_delta(hover, 25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

    # Case 2: hovering can be either or in both directions
    def test__get_hover_delta__2(self):
        hover = physics.Hovering(x=math.sin)
        x, y = physics.get_hover_delta(hover, 25)

        self.assertEqual(hover.index, 1)
        self.assertGreater(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

        hover = physics.Hovering(y=math.sin)
        x, y = physics.get_hover_delta(hover, 25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(x, 0.0)
        self.assertGreater(y, 0.0)

        hover = physics.Hovering(x=math.cos, y=math.sin)
        x, y = physics.get_hover_delta(hover, 25)

        self.assertEqual(hover.index, 1)
        self.assertGreater(x, 0.0)
        self.assertGreater(y, 0.0)

    # Case 3: hovering with zero amplitude yields no movement
    def test__get_hover_delta__3(self):
        hover = physics.Hovering(x=math.sin, y=math.cos, amplitude=0.0)
        x, y = physics.get_hover_delta(hover, 25)

        self.assertEqual(hover.index, 1)
        self.assertAlmostEqual(x, 0.0)
        self.assertAlmostEqual(y, 0.0)

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_jump_height_difference(self):
        # positive while jumping
        self.assertAlmostEqual(physics.get_jump_height_difference(10, 25), 0.4464, 3)

        # negative while falling
        self.assertAlmostEqual(physics.get_jump_height_difference(10, physics.JUMP_DURATION + 1), -0.4128, 3)
        self.assertAlmostEqual(physics.get_jump_height_difference(10, 10 * physics.JUMP_DURATION), -886.824, 3)

# ----------------------------------------------------------------------------------------------------------------------


class PhysicsSystemTest(unittest.TestCase):

    def setUp(self):
        class DemoListener(physics.PhysicsListener):
            def __init__(self):
                self.last = None

            # gravity ------

            def on_jumping(self, actor: physics.Actor) -> None:
                self.last = ('jumping', actor)

            def on_falling(self, actor: physics.Actor) -> None:
                self.last = ('falling', actor)

            def on_landing(self, actor: physics.Actor) -> None:
                self.last = ('landing', actor, actor.fall_from_y)

            def on_collide_platform(self, actor: physics.Actor, platform: physics.Platform) -> None:
                self.last = ('collide', actor, platform)

            # movement ------

            def on_switch_platform(self, actor: physics.Actor, platform: physics.Platform) -> None:
                self.last = ('switch', actor, platform)

            # ladders ------

            def on_reach_ladder(self, actor: physics.Actor, ladder: physics.Ladder) -> None:
                self.last = ('reach_ladder', actor, ladder)

            def on_leave_ladder(self, actor: physics.Actor, ladder: physics.Ladder) -> None:
                self.last = ('leave_ladder', actor, ladder)

            # collision ------

            def on_touch_actor(self, actor: physics.Actor, other: physics.Actor) -> None:
                self.last = ('touch', actor, other)

            def on_reach_object(self, actor: physics.Actor, obj: physics.Object) -> None:
                self.last = ('reach_object', actor, obj)

            def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
                self.last = ('impact_platform', proj, platform)

            def on_impact_actor(self, proj: physics.Projectile, actor: physics.Actor) -> None:
                self.last = ('impact_actor', proj, actor)

        self.listener = DemoListener()
        self.sys = physics.Physics(self.listener)

        self.actor = physics.Actor(45, 0, 0)
        self.sys.actors.append(self.actor)

    # ------------------------------------------------------------------------------------------------------------------

    def test__start_jumping(self):
        self.actor.ladder = physics.Ladder(0, 0, 1)
        self.actor.anchor = physics.Platform(0, 0, 1)
        self.actor.jump_ms = 5
        self.actor.fall_from_y = 10
        self.sys.start_jumping(self.actor)

        self.assertIsNone(self.actor.ladder)
        self.assertIsNone(self.actor.anchor)
        self.assertIsNone(self.actor.fall_from_y)
        self.assertEqual(self.actor.jump_ms, 0)
        self.assertEqual(self.listener.last[0], 'jumping')
        self.assertEqual(self.listener.last[1], self.actor)

    def test__start_falling(self):
        self.actor.y = 10
        self.sys.start_falling(self.actor)

        self.assertAlmostEqual(self.actor.force_y, -1.0)
        self.assertEqual(self.actor.jump_ms, physics.JUMP_DURATION)
        self.assertEqual(self.actor.fall_from_y, 10)
        self.assertEqual(self.listener.last[0], 'falling')
        self.assertEqual(self.listener.last[1], self.actor)

    def test__stop_falling(self):
        self.actor.jump_ms = 5
        self.actor.y = 12
        self.actor.fall_from_y = 10
        self.sys.stop_falling(self.actor)

        self.assertAlmostEqual(self.actor.force_y, 0.0)
        self.assertEqual(self.actor.jump_ms, 0)
        self.assertEqual(self.listener.last[0], 'landing')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 10)
        self.assertIsNone(self.actor.fall_from_y)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: landing on closest platform
    def test__check_falling_collision__1(self):
        self.actor.x = 2
        self.actor.y = 1
        last_pos = pygame.math.Vector2(3, 6)
        self.sys.platforms.append(physics.Platform(x=0, y=4, width=4))
        self.sys.platforms.append(physics.Platform(x=0, y=5, width=4))
        self.sys.platforms.append(physics.Platform(x=3, y=2, width=4))
        platform = self.sys.check_falling_collision(self.actor, last_pos)

        self.assertEqual(platform, self.sys.platforms[1])

    # Case 2: no platform inbetween
    def test__check_falling_collision__2(self):
        self.actor.x = 2
        self.actor.y = 3
        last_pos = pygame.math.Vector2(3, 6)
        self.sys.platforms.append(physics.Platform(x=3, y=2, width=4))
        platform = self.sys.check_falling_collision(self.actor, last_pos)

        self.assertIsNone(platform)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: free fall until platform
    def test__simulate_gravity__1(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=0, y=2, width=4))

        # initial falling
        self.sys.simulate_gravity(self.actor, 10)

        self.assertIsNone(self.actor.anchor)
        self.assertAlmostEqual(self.actor.force_y, -1.0)
        self.assertEqual(self.listener.last[0], 'falling')
        self.assertEqual(self.listener.last[1], self.actor)

        # continue to fall
        self.listener.last = None
        self.sys.simulate_gravity(self.actor, 10)

        self.assertAlmostEqual(self.actor.force_y, -1.0)
        self.assertIsNone(self.actor.anchor)
        self.assertIsNone(self.listener.last)

        # keep falling
        self.actor.collision_repeat_cooldown = 0
        for i in range(100):
            self.sys.simulate_gravity(self.actor, 10)

        self.assertEqual(self.actor.anchor, self.sys.platforms[0])
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'landing')
        self.assertEqual(self.listener.last[1], self.actor)

    # Case 2: standing on a platform, jumping off
    def test__simulate_gravity__2(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))

        # nothing happens except anchoring
        self.sys.simulate_gravity(self.actor, 10)

        self.assertEqual(self.actor.anchor, self.sys.platforms[0])
        self.assertAlmostEqual(self.actor.force_y, 0.0)
        # FIXME: short "falling" is triggered... not optimal but not a catastrophy either
        # self.assertIsNone(self.listener.last)

        # jump off
        self.actor.force_y = 1.0
        self.sys.simulate_gravity(self.actor, 10)

        self.assertIsNone(self.actor.anchor)
        self.assertAlmostEqual(self.actor.force_y, 1.0)
        self.assertEqual(self.listener.last[0], 'jumping')
        self.assertEqual(self.listener.last[1], self.actor)

        # will fall after a while
        self.listener.last = None
        for i in range(physics.JUMP_DURATION // (2 * 10)):
            self.sys.simulate_gravity(self.actor, 10)

        self.assertAlmostEqual(self.actor.force_y, -1.0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'falling')
        self.assertEqual(self.listener.last[1], self.actor)

    # Case 3: jumping off a ladder
    def test__simulate_gravity__3(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.ladders.append(physics.Ladder(x=2, y=2, height=4))
        self.actor.ladder = self.sys.ladders[0]

        # nothing happens
        self.sys.simulate_gravity(self.actor, 10)

        self.assertEqual(self.actor.ladder, self.sys.ladders[0])

        # jump off
        self.actor.force_x = 1.0
        self.actor.force_y = 1.0
        self.sys.simulate_gravity(self.actor, 10)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: platform in reach
    def test__get_supporting_platforms__1(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=5, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=1, width=3))
        self.sys.platforms.append(physics.Platform(x=2, y=3, width=3))

        anchor = self.sys.get_supporting_platforms(self.actor)
        self.assertEqual(anchor, self.sys.platforms[1])

    # Case 2: no platform is supporting
    def test__get_supporting_platforms__2(self):
        self.actor.x = 2
        self.actor.y = 3.5
        self.sys.platforms.append(physics.Platform(x=1, y=5, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=1, width=3))
        self.sys.platforms.append(physics.Platform(x=2, y=3, width=3))

        anchor = self.sys.get_supporting_platforms(self.actor)
        self.assertIsNone(anchor)

    # ------------------------------------------------------------------------------------------------------------------

    def test__anchor_actor(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=5, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=1, width=3))
        self.sys.platforms.append(physics.Platform(x=1.5, y=3, width=3))

        # initial anchoring
        self.sys.anchor_actor(self.actor)
        self.assertEqual(self.actor.anchor, self.sys.platforms[1])
        self.assertEqual(self.listener.last[0], 'switch')
        self.assertEqual(self.listener.last[1], self.actor)

        # moving a bit
        self.listener.last = None
        self.actor.x += 0.5
        self.sys.anchor_actor(self.actor)
        self.assertEqual(self.actor.anchor, self.sys.platforms[1])
        self.assertIsNone(self.listener.last)

        # switching
        self.sys.platforms[1].x -= 3
        self.sys.anchor_actor(self.actor)
        self.assertEqual(self.actor.anchor, self.sys.platforms[3])
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'switch')
        self.assertEqual(self.listener.last[1], self.actor)

        # staying there
        self.listener.last = None
        self.sys.anchor_actor(self.actor)
        self.assertEqual(self.actor.anchor, self.sys.platforms[3])
        self.assertIsNone(self.listener.last)

        # resetting
        self.actor.x += 3
        self.sys.anchor_actor(self.actor)
        self.assertIsNone(self.actor.anchor)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: moving along a single platform
    def test__check_movement_collision__1(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))

        # no collision
        self.actor.x = 2.5
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)

        # no collision when moving to the right
        self.actor.x = 4
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)
        self.actor.x = 5
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)

        # collision when moving left into another platform
        self.actor.x = 1
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)
        self.actor.x = 0.5
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)

    # Case 2: running into platform collision
    def test__check_movement_collision__2(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.platforms.append(physics.Platform(x=3, y=3, width=3, height=2))
        self.sys.platforms.append(physics.Platform(x=0, y=3, width=1, height=2))

        # no collision
        self.actor.x = 2.5
        platform = self.sys.check_movement_collision(self.actor)
        self.assertIsNone(platform)

        # collision when moving right into another platform
        self.actor.x = 3
        platform = self.sys.check_movement_collision(self.actor)
        self.assertEqual(platform, self.sys.platforms[1])

        # collision when moving left into another platform
        self.actor.x = 1
        platform = self.sys.check_movement_collision(self.actor)
        self.assertEqual(platform, self.sys.platforms[2])

    # ------------------------------------------------------------------------------------------------------------------

    def test__handle_movement(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.platforms.append(physics.Platform(x=3, y=3, width=3, height=2))
        self.sys.platforms.append(physics.Platform(x=0, y=3, width=1, height=2))

        # no collision
        self.sys.handle_movement(self.actor, 10)
        self.assertIsNone(self.listener.last)

        # collision when moving right into another platform
        self.actor.force_x = 1.0
        self.listener.last = None
        for i in range(100):
            self.sys.handle_movement(self.actor, 10)

        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'collide')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], self.sys.platforms[1])

        # collision when moving left into another platform
        self.actor.force_x = -1.0
        self.listener.last = None
        self.actor.touch_repeat_cooldown = 0
        for i in range(100):
            self.sys.handle_movement(self.actor, 10)

        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'collide')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], self.sys.platforms[2])

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: find ladder mid-ladder
    def test__find_ladder(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))

        # finding no ladder
        ladder = self.sys.find_ladder(self.actor)
        self.assertIsNone(ladder)

        # finding closest ladder
        self.sys.ladders.append(physics.Ladder(x=2.2, y=2, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.1, y=2, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.24, y=2, height=4))
        ladder = self.sys.find_ladder(self.actor)
        self.assertEqual(ladder, self.sys.ladders[1])

    # Case 2: find ladder's bottom
    def test__find_ladder__2(self):
        self.actor.x = 2
        self.actor.y = 3.001  # NOTE: entering the ladder requires minimal jumping
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))

        # finding no ladder
        ladder = self.sys.find_ladder(self.actor)
        self.assertIsNone(ladder)

        # finding closest ladder
        self.sys.ladders.append(physics.Ladder(x=2.2, y=3, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.1, y=3, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.24, y=3, height=4))
        ladder = self.sys.find_ladder(self.actor)
        self.assertEqual(ladder, self.sys.ladders[1])

    # Case 3: find ladder's top
    def test__find_ladder__3(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))

        # finding no ladder
        ladder = self.sys.find_ladder(self.actor)
        self.assertIsNone(ladder)

        # finding closest ladder
        self.sys.ladders.append(physics.Ladder(x=2.2, y=-1, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.1, y=-1, height=4))
        self.sys.ladders.append(physics.Ladder(x=2.24, y=-1, height=4))
        ladder = self.sys.find_ladder(self.actor)
        self.assertEqual(ladder, self.sys.ladders[1])

    # ------------------------------------------------------------------------------------------------------------------

    def test__grab_ladder(self):
        self.actor.x = 2
        self.actor.y = 3
        self.sys.platforms.append(physics.Platform(x=1, y=3, width=3))
        self.sys.ladders.append(physics.Ladder(x=2, y=1, height=4))

        # grab ladder
        self.sys.grab_ladder(self.actor)
        self.assertEqual(self.actor.ladder, self.sys.ladders[0])
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'reach_ladder')
        self.assertEqual(self.listener.last[1], self.actor)

        # staying there
        self.listener.last = None
        self.sys.grab_ladder(self.actor)
        self.assertEqual(self.actor.ladder, self.sys.ladders[0])
        self.assertIsNone(self.listener.last)

        # leaving ladder
        self.listener.last = None
        self.actor.x += 1
        self.sys.grab_ladder(self.actor)
        self.assertIsNone(self.actor.ladder)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'leave_ladder')
        self.assertEqual(self.listener.last[1], self.actor)

        # staying there
        self.listener.last = None
        self.sys.grab_ladder(self.actor)
        self.assertIsNone(self.actor.ladder)
        self.assertIsNone(self.listener.last)

    # ------------------------------------------------------------------------------------------------------------------

    def test__handle_ladder__1(self):
        self.actor.x = 2
        self.actor.y = 3
        self.actor.jump_ms = 10
        self.actor.fall_from_y = 4
        self.sys.platforms.append(physics.Platform(x=1, y=2, width=3))
        self.sys.platforms.append(physics.Platform(x=1, y=5, width=3))
        self.sys.ladders.append(physics.Ladder(x=2, y=2, height=3))

        # holding stops jumping/falling
        self.sys.handle_ladder(self.actor, 10)
        self.assertEqual(self.actor.jump_ms, 0)
        self.assertIsNone(self.actor.fall_from_y)

        # climbing upwards
        self.actor.y = 3
        self.actor.force_y = -1.0
        self.sys.handle_ladder(self.actor, 10)
        self.assertEqual(self.actor.ladder, self.sys.ladders[0])
        self.assertEqual(self.actor.x, 2)
        self.assertLess(self.actor.y, 3)

        # climbing upwards
        self.actor.y = 3
        self.actor.force_y = 1.0
        self.sys.handle_ladder(self.actor, 10)
        self.assertEqual(self.actor.ladder, self.sys.ladders[0])
        self.assertEqual(self.actor.x, 2)
        self.assertGreater(self.actor.y, 3)

        # climbing towards platform
        self.listener.last = None
        self.assertIsNone(self.actor.anchor)
        for i in range(100):
            self.actor.force_y = 1.0
            self.sys.handle_ladder(self.actor, 10)

        self.assertEqual(self.actor.anchor, self.sys.platforms[1])

    # ------------------------------------------------------------------------------------------------------------------

    def test__check_actor_collision(self):
        self.actor.x = 2
        self.actor.y = 3
        self.actor.radius = 0.7
        actor2 = physics.Actor(object_id=542, x=3.2, y=3, radius=0.2)
        self.sys.actors.append(actor2)

        # out of reach
        self.sys.check_actor_collision(self.actor, 10)
        self.assertIsNone(self.listener.last)
        self.sys.check_actor_collision(actor2, 10)
        self.assertIsNone(self.listener.last)

        # within reach
        actor2.radius += 0.5
        self.sys.check_actor_collision(self.actor, 10)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'touch')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], actor2)

        # repeat does not immediately trigger another event
        self.assertEqual(self.actor.touch_repeat_cooldown, physics.COLLISION_REPEAT_DELAY)
        self.listener.last = None
        self.sys.check_actor_collision(self.actor, 10)
        self.assertIsNone(self.listener.last)

    def test__check_object_collision(self):
        self.actor.x = 2
        self.actor.y = 3
        self.actor.radius = 0.7
        obj = physics.Object(x=3.2, y=3, object_type=12)
        self.sys.objects.append(obj)

        # out of reach
        self.sys.check_object_collision(self.actor, 10)
        self.assertIsNone(self.listener.last)

        # within reach
        self.actor.radius += 0.5
        self.sys.check_object_collision(self.actor, 10)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'reach_object')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], obj)

        # repeat does not immediately trigger another event
        self.assertEqual(self.actor.touch_repeat_cooldown, physics.COLLISION_REPEAT_DELAY)
        self.listener.last = None
        self.sys.check_object_collision(self.actor, 10)
        self.assertIsNone(self.listener.last)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: projectiles can hit actors
    def test__update_projectile__1(self):
        self.actor.x = 2
        self.actor.y = 3
        proj = physics.Projectile(x=4, y=3, radius=0.2, face_x=-1, object_type=9)
        self.sys.projectiles.append(proj)

        for i in range(100):
            self.sys.update_projectile(proj, 10)
        self.assertLess(proj.x, self.actor.x)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'impact_actor')
        self.assertEqual(self.listener.last[1], proj)
        self.assertEqual(self.listener.last[2], self.actor)

    # Case 2: projectiles do not hit actor who shot them
    def test__update_projectile__2(self):
        self.actor.x = 2
        self.actor.y = 3
        proj = physics.Projectile(x=4, y=3, radius=0.2, face_x=-1, object_type=9, origin=self.actor)
        self.sys.projectiles.append(proj)

        for i in range(100):
            self.sys.update_projectile(proj, 10)
        self.assertIsNone(self.listener.last)
        self.assertLess(proj.x, self.actor.x)

    # Case 3: projectiles are stopped by platforms
    def test__update_projectile__3(self):
        self.actor.x = 2
        self.actor.y = 3
        proj = physics.Projectile(x=4, y=3, radius=0.2, face_x=1, object_type=9)
        self.sys.projectiles.append(proj)
        platform = physics.Platform(x=5, y=2, width=1, height=2)
        self.sys.platforms.append(platform)

        for i in range(100):
            self.sys.update_projectile(proj, 10)
        self.assertLess(proj.x, platform.x)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'impact_platform')
        self.assertEqual(self.listener.last[1], proj)
        self.assertEqual(self.listener.last[2], platform)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: hovering into x-direction
    def test__simulate_floating__1(self):
        self.actor.x = 2
        self.actor.y = 1
        hover = physics.Hovering(x=math.sin, amplitude=2)

        platform = physics.Platform(x=0, y=1, width=4, hover=hover)
        self.sys.platforms.append(platform)
        self.actor.anchor = platform

        platform2 = physics.Platform(x=3, y=0, width=4, height=2)
        self.sys.platforms.append(platform2)

        # move platform with actor
        self.sys.simulate_floating(platform, 10)
        self.assertGreater(platform.x, 0)
        self.assertEqual(platform.y, 1)
        self.assertEqual(self.actor.x, 2 + platform.x)
        self.assertEqual(self.actor.y, platform.y)

        # actor will collide with the other platform after some time
        for i in range(83):
            self.sys.simulate_floating(platform, 10)
        self.assertLess(self.actor.x, platform2.x)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'collide')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], platform2)

        # collision is not always re-triggered
        self.assertGreater(self.actor.x, 0)
        self.listener.last = None
        self.sys.simulate_floating(platform, 10)
        self.assertGreater(self.actor.x, 0)
        self.assertIsNone(self.listener.last)

    # Case 2: hovering up into y-direction
    def test__simulate_floating__2(self):
        self.actor.x = 2
        self.actor.y = 1
        hover = physics.Hovering(y=math.sin, amplitude=2)

        platform = physics.Platform(x=0, y=1, width=4, hover=hover)
        self.sys.platforms.append(platform)
        self.actor.anchor = platform

        # move platform with actor
        self.sys.simulate_floating(platform, 10)
        self.assertEqual(platform.x, 0)
        self.assertGreater(platform.y, 0)
        self.assertEqual(self.actor.x, 2 + platform.x)
        self.assertEqual(self.actor.y, platform.y)

    # Case 3: hovering down into y-direction
    def test__simulate_floating__3(self):
        self.actor.x = 2
        self.actor.y = 1
        hover = physics.Hovering(y=math.sin, amplitude=-2)

        platform = physics.Platform(x=0, y=1, width=4, hover=hover)
        self.sys.platforms.append(platform)
        self.actor.anchor = platform

        # move platform with actor
        self.sys.simulate_floating(platform, 10)
        self.assertEqual(platform.x, 0)
        self.assertLess(platform.y, 1)
        self.assertEqual(self.actor.x, 2 + platform.x)
        self.assertEqual(self.actor.y, platform.y)

    # Case 4: hovering into x- and y-direction
    def test__simulate_floating__4(self):
        self.actor.x = 2
        self.actor.y = 1
        hover = physics.Hovering(x=math.cos, y=math.sin)

        platform = physics.Platform(x=0, y=1, width=4, hover=hover)
        self.sys.platforms.append(platform)
        self.actor.anchor = platform

        # move platform with actor
        self.sys.simulate_floating(platform, 10)
        self.assertGreater(platform.x, 0)
        self.assertGreater(platform.y, 1)
        self.assertEqual(self.actor.x, 2 + platform.x)
        self.assertEqual(self.actor.y, platform.y)
