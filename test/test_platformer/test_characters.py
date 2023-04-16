import unittest
import pygame
from typing import Optional

from platformer import characters
from platformer import physics


class CharacterFunctionsTest(unittest.TestCase):

    def test__get_falling_damage(self):
        # falling damage is getting larger
        self.assertEqual(characters.get_falling_damage(3.9), 0)
        d1 = characters.get_falling_damage(4.0)
        self.assertEqual(d1, 1)
        d2 = characters.get_falling_damage(8.0)
        self.assertGreater(d2, d1)
        d3 = characters.get_falling_damage(250.0)
        self.assertGreater(d3, d2)

    def test__modify_hitpoint(self):
        actor = characters.Actor(object_id=5)

        characters.modify_hitpoints(actor, -2)
        self.assertEqual(actor.hit_points, 3)

        characters.modify_hitpoints(actor, 1)
        self.assertEqual(actor.hit_points, 4)

        # never exceed maximum
        characters.modify_hitpoints(actor, 100)
        self.assertEqual(actor.hit_points, 5)

        # never exceeds zero
        characters.modify_hitpoints(actor, -6)
        self.assertEqual(actor.hit_points, 0)

# ----------------------------------------------------------------------------------------------------------------------


class CharacterSystemTest(unittest.TestCase):

    def setUp(self):
        class DemoListener(characters.EventListener):
            def __init__(self):
                self.last = None

            def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
                self.last = ('damaged', actor, damage, cause)

            def on_char_died(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
                self.last = ('died', actor, damage, cause)

        self.listener = DemoListener()
        self.sys = characters.Characters(self.listener)

        self.actor = characters.Actor(45)
        self.sys.characters.append(self.actor)

    # ------------------------------------------------------------------------------------------------------------------

    def test_apply_damage(self):
        # anonymous damage can harm
        self.sys.apply_damage(self.actor, 2)
        self.assertEqual(self.actor.hit_points, 3)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'damaged')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 2)
        self.assertIsNone(self.listener.last[3])

        # another char's damage can harm
        self.listener.last = None
        actor2 = characters.Actor(24)
        self.sys.apply_damage(self.actor, 2, actor2)
        self.assertEqual(self.actor.hit_points, 1)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'damaged')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 2)
        self.assertEqual(self.listener.last[3], actor2)

        # anonymous damage can kill
        self.listener.last = None
        self.sys.apply_damage(self.actor, 2)
        self.assertEqual(self.actor.hit_points, 0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'died')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 2)
        self.assertIsNone(self.listener.last[3])

        # another char's damage can harm
        self.listener.last = None
        self.actor.hit_points = 1
        actor2 = characters.Actor(24)
        self.sys.apply_damage(self.actor, 2, actor2)
        self.assertEqual(self.actor.hit_points, 0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'died')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 2)
        self.assertEqual(self.listener.last[3], actor2)

        # dead man cannot be harmed anymore
        self.listener.last = None
        actor2 = characters.Actor(24)
        self.sys.apply_damage(self.actor, 2, actor2)
        self.assertEqual(self.actor.hit_points, 0)
        self.assertIsNone(self.listener.last)

    # ------------------------------------------------------------------------------------------------------------------

    def test__apply_projectile_hit(self):
        proj = physics.Projectile(pos=pygame.math.Vector2(0, 0), radius=0.5)

        # anonymous projectile can hit actor
        self.sys.apply_projectile_hit(self.actor, 2, proj)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'damaged')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 2)
        self.assertIsNone(self.listener.last[3])

        # another char's projectile can hit actor
        self.listener.last = None
        actor2 = characters.Actor(13)
        self.sys.characters.append(actor2)
        proj.from_actor = actor2
        self.sys.apply_projectile_hit(self.actor, 1, proj)
        self.assertEqual(self.actor.hit_points, 2)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'damaged')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 1)
        self.assertEqual(self.listener.last[3], actor2)

        # another char's projectile can kill actor
        self.listener.last = None
        self.actor.hit_points = 1
        self.sys.apply_projectile_hit(self.actor, 1, proj)
        self.assertEqual(self.actor.hit_points, 0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'died')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 1)
        self.assertEqual(self.listener.last[3], actor2)

        # anonymous can kill actor
        proj.from_actor = None
        self.listener.last = None
        self.actor.hit_points = 1
        self.sys.apply_projectile_hit(self.actor, 1, proj)
        self.assertEqual(self.actor.hit_points, 0)
        self.assertIsInstance(self.listener.last, tuple)
        self.assertEqual(self.listener.last[0], 'died')
        self.assertEqual(self.listener.last[1], self.actor)
        self.assertEqual(self.listener.last[2], 1)
        self.assertIsNone(self.listener.last[3])

