import unittest

from core import bounded_value


class BoundedValueTest(unittest.TestCase):

    def test__modify(self):
        container = bounded_value.Int(5, 10)
        self.assertEqual(container.value, 5)
        self.assertEqual(container.max_value, 10)

        container.value = 7
        self.assertEqual(container.value, 7)
        self.assertEqual(container.max_value, 10)

        container.value += 2
        self.assertEqual(container.value, 9)
        self.assertEqual(container.max_value, 10)

        # cannot exceed max
        container.value += 2
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        container.value -= 7
        self.assertEqual(container.value, 3)
        self.assertEqual(container.max_value, 10)

        # cannot exceed 0
        container.value -= 7
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # add number
        container = container + 2
        self.assertEqual(container.value, 2)
        self.assertEqual(container.max_value, 10)

        # add number never exceeds
        container = container + 12
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        # iadd number
        container.value = 1
        container += 3
        self.assertEqual(container.value, 4)
        self.assertEqual(container.max_value, 10)

        # iadd number never exceeds
        container += 12
        self.assertEqual(container.value, 10)
        self.assertEqual(container.max_value, 10)

        # sub number
        container.value = 5
        container = container - 2
        self.assertEqual(container.value, 3)
        self.assertEqual(container.max_value, 10)

        # sub number never exceeds
        container = container - 4
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # isub number
        container.value = 3
        container -= 2
        self.assertEqual(container.value, 1)
        self.assertEqual(container.max_value, 10)

        # isub number never exceeds
        container -= 2
        self.assertEqual(container.value, 0)
        self.assertEqual(container.max_value, 10)

        # comparision
        container.value = 4
        self.assertTrue(container == 4)
        self.assertFalse(container != 4)
        self.assertTrue(container < 5)
        self.assertTrue(container <= 5)
        self.assertTrue(container > 3)
        self.assertTrue(container >= 3)


"""
    def test__get_falling_damage(self):
        # falling damage is getting larger
        self.assertEqual(characters.get_falling_damage(3.9), 0)
        d1 = characters.get_falling_damage(4.0)
        self.assertEqual(d1, 1)
        d2 = characters.get_falling_damage(8.0)
        self.assertGreater(d2, d1)
        d3 = characters.get_falling_damage(250.0)
        self.assertGreater(d3, d2)


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
        proj = physics.Projectile(object_id=10, pos=pygame.math.Vector2(0, 0), radius=0.5)

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

"""
