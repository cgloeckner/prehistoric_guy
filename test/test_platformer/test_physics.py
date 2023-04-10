import unittest
import pygame
import math

from platformer import physics


class PhysicsFunctionsTest(unittest.TestCase):

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

    # Case 1: regular intersection
    def test__test_line_intersection(self):
        pos = physics.test_line_intersection(0, 1, 10, 0, 4, -3, 6, 7)
        self.assertIsNotNone(pos)
        self.assertAlmostEqual(pos[0], 4.706, places=2)
        self.assertAlmostEqual(pos[1], 0.529, places=2)

    # Case 2: lines do not cross yet (one ends too early)
    def test__test_line_intersection__2(self):
        pos = physics.test_line_intersection(0, 1, 10, 0, 4, -3, 6, -1)
        self.assertIsNone(pos)

        pos = physics.test_line_intersection(4, -3, 6, -1, 0, 1, 10, 0)
        self.assertIsNone(pos)

    # Case 3: lines do not intersect if parallel
    def test__test_line_intersection__3(self):
        pos = physics.test_line_intersection(0, 1, 1, 0, 0, -2, 1, -2)
        self.assertIsNone(pos)

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: position inside platform
    # NOTE: y is the top, so y - height leads to the bottom
    def test__is_inside_platform__1(self):
        plat = physics.Platform(3, 2, 10, 5)

        self.assertTrue(physics.is_inside_platform(4, -1, plat))

    # Case 2: position at platform's top
    def test__is_inside_platform__2(self):
        plat = physics.Platform(3, 2, 10, 5)

        # top/bottom/left/right edges do not belong to platform
        self.assertFalse(physics.is_inside_platform(4, 2, plat))
        self.assertFalse(physics.is_inside_platform(4, 7, plat))
        self.assertFalse(physics.is_inside_platform(3, 5, plat))
        self.assertFalse(physics.is_inside_platform(13, 5, plat))

    # Case 3: position outside platform
    def test__is_inside_platform__3(self):
        plat = physics.Platform(3, 2, 10, 5)

        # above/below/left/right
        self.assertFalse(physics.is_inside_platform(4, 3, plat))
        self.assertFalse(physics.is_inside_platform(4, 8, plat))
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

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: points within ladder
    # NOTE: y is the bottom, so y + height leads to the bottom
    def test__ladder_in_reach__1(self):
        ladder = physics.Ladder(2, 3, 4)

        # top/mid/bottom end are in reach
        # NOTE: ladder's x is left, not center (2.5)
        self.assertTrue(physics.ladder_in_reach(2.5, 3, ladder))
        self.assertTrue(physics.ladder_in_reach(2.5, 4, ladder))
        self.assertTrue(physics.ladder_in_reach(2.5, 7, ladder))

    # Case 2: points within ladder +/- radius
    def test__ladder_in_reach__2(self):
        ladder = physics.Ladder(2, 3, 4)

        self.assertTrue(physics.ladder_in_reach(2.5 - physics.OBJECT_RADIUS, 4, ladder))
        self.assertTrue(physics.ladder_in_reach(2.5 + physics.OBJECT_RADIUS - 0.001, 4, ladder))

    # Case 3: points outside ladder +/- radius
    def test__ladder_in_reach__3(self):
        ladder = physics.Ladder(2, 3, 4)

        # top/bottom
        self.assertFalse(physics.ladder_in_reach(2.5, 3 - physics.OBJECT_RADIUS, ladder))
        self.assertFalse(physics.ladder_in_reach(2.5, 8 + physics.OBJECT_RADIUS, ladder))

        # left/right
        self.assertFalse(physics.ladder_in_reach(2.5 - physics.OBJECT_RADIUS - 0.001, 4, ladder))
        self.assertFalse(physics.ladder_in_reach(2.5 + physics.OBJECT_RADIUS, 4, ladder))

    # ------------------------------------------------------------------------------------------------------------------

    # Case 1: actor in the middle
    def test__within_ladder__1(self):
        ladder = physics.Ladder(2, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=4.25, ladder=ladder)

        self.assertTrue(physics.within_ladder(actor))

    # Case 2: actor at the top
    def test__within_ladder__2(self):
        ladder = physics.Ladder(2, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=7, ladder=ladder)

        self.assertFalse(physics.within_ladder(actor))

    # Case 3: actor at the bottom
    def test__within_ladder__3(self):
        ladder = physics.Ladder(2, 3, 4)
        actor = physics.Actor(object_id=13, x=2.5, y=2, ladder=ladder)

        self.assertFalse(physics.within_ladder(actor))

    # Case 3: actor without ladder
    def test__within_ladder__3(self):
        actor = physics.Actor(object_id=13, x=2.5, y=4.25)

        self.assertFalse(physics.within_ladder(actor))

    # ------------------------------------------------------------------------------------------------------------------

    def test__get_jump_height_difference(self):
        # positive while jumping
        self.assertAlmostEqual(physics.get_jump_height_difference(10, 25), 0.4464, 3)

        # negative while falling
        self.assertAlmostEqual(physics.get_jump_height_difference(10, physics.JUMP_DURATION + 1), -0.4128, 3)
        self.assertAlmostEqual(physics.get_jump_height_difference(10, 10 * physics.JUMP_DURATION), -886.824, 3)

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

# ----------------------------------------------------------------------------------------------------------------------

class PhysicsSystemTest(unittest.TestCase):

    def setUp(self):
        class DemoListener(physics.PhysicsListener):
            def __init__(self):
                self.last = None

            def on_falling(self, actor: physics.Actor) -> None:
                self.last = ['falling', actor]

            def on_land_on_platform(self, actor: physics.Actor, platform: physics.Platform) -> None:
                self.last = ['land', actor, platform]

            def on_collide_platform(self, actor: physics.Actor, platform: physics.Platform) -> None:
                self.last = ['collide', actor, platform]

            def on_switch_platform(self, actor: physics.Actor, platform: physics.Platform) -> None:
                self.last = ['switch', actor, platform]

            def on_touch_actor(self, actor: physics.Actor, other: physics.Actor) -> None:
                self.last = ['touch', actor, other]

            def on_reach_object(self, actor: physics.Actor, obj: physics.Object) -> None:
                self.last = ['reach_object',actor, obj]

            def on_reach_ladder(self, actor: physics.Actor, ladder: physics.Ladder) -> None:
                self.last = ['reach_ladder', actor, ladder]

            def on_leave_ladder(self, actor: physics.Actor, ladder: physics.Ladder) -> None:
                self.last = ['leave', actor, ladder]

            def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
                self.last = ['impact_platform', proj, platform]

            def on_impact_actor(self, proj: physics.Projectile, actor: physics.Actor) -> None:
                self.last = ['import_actor', proj, actor]

        self.listener = DemoListener()
        self.sys = physics.Physics(self.listener)

        self.actor = physics.Actor(45, 2, 3)
        self.sys.actors.append(self.actor)

    # ------------------------------------------------------------------------------------------------------------------

    # FIXME: test__get_by_id
    # FIXME: test__get_supporting_platforms
    # FIXME: test__anchor_actor
    # FIXME: test__find_closest_ladder
    # FIXME: test__grab_ladder
    # FIXME: test__is_falling
    # FIXME: test__check_falling_collision
    # FIXME: test__check_movement_collision
    # FIXME: test__simulate_gravity
    # FIXME: test__handle_movement
    # FIXME: test__handle_climb
    # FIXME: test__check_actor_collision
    # FIXME: test__check_object_collision
    # FIXME: test__simulate_floating
    # FIXME: test__update_projectile
