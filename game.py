import random
import math
from typing import Optional

import platformer


def get_falling_damage(height: float) -> int:
    """Calculates falling damage based on falling height.
    Returns integer damage.
    """
    return int(height / 4.0)


class Manager(platformer.PhysicsListener, platformer.AnimationListener):

    def __init__(self):
        self.factory: Optional[platformer.ObjectManager] = None

        self.player_character = None
        self.enemies = list()

    def create_random_object(self) -> None:
        # pick random position on random platform
        p = random.choice(self.factory.physics.platforms)
        x = random.randrange(p.width)

        self.factory.create_object(x=p.x + x, y=p.y + 0.5, object_type=random.randrange(platformer.MAX_OBJECT_TYPE))

    def populate_demo_scene(self, cache: platformer.Cache) -> None:
        generic_guy = cache.get_sprite_sheet('guy')
        blue_guy = cache.get_hsl_transformed(generic_guy, platformer.HslTransform(hue=0.6),
                                             platformer.SPRITE_CLOTHES_COLORS)
        grey_guy = cache.get_hsl_transformed(generic_guy, platformer.HslTransform(saturation=0.0),
                                             platformer.SPRITE_CLOTHES_COLORS)

        self.player_character = self.factory.create_character(sprite_sheet=blue_guy, x=2, y=5)
        self.enemies.append(self.factory.create_character(sprite_sheet=grey_guy, x=6.5, y=6.5))
        self.enemies.append(self.factory.create_character(sprite_sheet=grey_guy, x=6.5, y=4.5))

        # horizontal platforms
        self.factory.create_platform(x=0, y=1, width=3, height=2)
        self.factory.create_platform(x=2, y=2, width=2)
        self.factory.create_platform(x=0, y=4, width=3)
        self.factory.create_platform(x=6, y=1, width=3)
        self.factory.create_platform(x=4, y=4, width=1, height=11)
        self.factory.create_platform(x=5, y=6, width=4)

        self.factory.create_platform(x=3, y=6, width=1, hover=platformer.Hovering(x=math.cos, amplitude=-2))

        # ladders
        self.factory.create_ladder(x=1, y=1, height=7)
        self.factory.create_ladder(x=8, y=1, height=5)

        self.create_random_object()

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_land_on_platform(self, actor: platformer.Actor, platform: platformer.Platform) -> None:
        """Triggered when the actor landed on a platform.
        """
        # search corresponding animation
        for sprite in self.factory.renderer.sprites:
            if sprite.actor == actor:
                action = platformer.IDLE_ACTION
                delta_h = actor.fall_from_y - sprite.actor.y
                damage = get_falling_damage(delta_h)

                if delta_h > 1.5:
                    action = platformer.LANDING_ACTION

                    # find character
                    relevant = [c for c in self.factory.characters if c.sprite.actor == actor]
                    if len(relevant) > 0:
                        c = relevant[0]
                        c.hit_points -= damage
                        if damage > 0:
                            # FIXME: on_player_wounded
                            platformer.flash(sprite.animation, platformer.HslTransform(lightness=1.0), 200)
                            if c.hit_points <= 0:
                                action = platformer.DIE_ACTION

                platformer.start(sprite.animation, action)
                return

    def on_falling(self, actor: platformer.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        pass

    def on_collide_platform(self, actor: platformer.Actor, platform: platformer.Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        pass

    def on_switch_platform(self, actor: platformer.Actor, platform: platformer.Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        pass

    def on_touch_actor(self, actor: platformer.Actor, other: platformer.Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        pass

    def on_reach_object(self, actor: platformer.Actor, obj: platformer.Object) -> None:
        """Triggered when the actor reaches an object.
        """
        # find character
        relevant = [c for c in self.factory.characters if c.sprite.actor == actor]
        if len(relevant) > 0:
            if obj.object_type == platformer.FOOD_OBJ:
                # heal him
                relevant[0].hit_points += 1
                # FIXME: on_player_healed

            elif obj.object_type == platformer.WEAPON_OBJ:
                # grab axe
                relevant[0].num_axes += 1
                # FIXME: on_weapon_collected

        self.factory.destroy_object(obj)
        self.create_random_object()

    def on_reach_ladder(self, actor: platformer.Actor, ladder: platformer.Ladder) -> None:
        """Triggered when the actor reaches a ladder.
        """
        pass

    def on_leave_ladder(self, actor: platformer.Actor, ladder: platformer.Ladder) -> None:
        """Triggered when the actor leaves a ladder.
        """
        pass

    # --- Animation Events -

    def on_step(self, ani: platformer.Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        pass

    def on_climb(self, ani: platformer.Animation) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        pass

    def on_attack(self, ani: platformer.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        pass

    def on_throw(self, ani: platformer.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        relevant = [c for c in self.factory.characters if c.sprite.animation == ani]
        if len(relevant) == 0:
            return

        character = relevant[0]
        if character.num_axes == 0:
            return

        character.num_axes -= 1
        sprite = character.sprite
        self.factory.create_projectile(origin=sprite.actor, x=sprite.actor.x,
                                       y=sprite.actor.y + sprite.actor.radius, radius=platformer.OBJECT_RADIUS,
                                       face_x=sprite.actor.face_x, object_type=platformer.WEAPON_OBJ)

    def on_impact_platform(self, proj: platformer.Projectile, platform: platformer.Platform) -> None:
        """Triggered when a projectile hits a platform.
        """
        self.factory.create_object(x=proj.x, y=proj.y - platformer.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)

    def on_impact_actor(self, proj: platformer.Projectile, actor: platformer.Actor) -> None:
        """Triggered when a projectile hits an actor.
        """
        sprite = [sprite for sprite in self.factory.renderer.sprites if sprite.actor == actor][0]
        self.factory.destroy_sprite(sprite)
        self.factory.create_object(x=proj.x, y=proj.y - platformer.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)
