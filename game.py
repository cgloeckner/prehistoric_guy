import pygame
import random
import math
from typing import Optional

from constants import *
import platforms
import animations
import factory


def get_falling_damage(height: float) -> int:
    """Calculates falling damage based on falling height.
    Returns integer damage.
    """
    return int(height / 4.0)


class Manager(platforms.PhysicsListener, animations.AnimationListener):

    def __init__(self):
        self.factory: Optional[factory.ObjectManager] = None

        self.player_character = None
        self.enemies = list()

    def create_food(self) -> None:
        # pick random position on random platform
        p = random.choice(self.factory.physics.platforms)
        x = random.randrange(p.width)

        self.factory.create_object(x=p.x + x, y=p.y + 0.5, object_type=FOOD_OBJ)

    def populate_demo_scene(self, guy_sheet: pygame.Surface) -> None:
        self.player_character = self.factory.create_character(sprite_sheet=guy_sheet, x=2, y=5)
        self.enemies.append(self.factory.create_character(sprite_sheet=guy_sheet, x=6.5, y=6.5))
        self.enemies.append(self.factory.create_character(sprite_sheet=guy_sheet, x=6.5, y=4.5))

        # horizontal platforms
        self.factory.create_platform(x=0, y=1, width=3, height=2)
        self.factory.create_platform(x=2, y=2, width=2)
        self.factory.create_platform(x=0, y=4, width=3)
        self.factory.create_platform(x=6, y=1, width=3)
        self.factory.create_platform(x=4, y=4, width=1, height=11)
        self.factory.create_platform(x=5, y=6, width=4)

        self.factory.create_platform(x=3, y=6, width=1, hover=platforms.Hovering(x=math.cos, amplitude=-2))

        # ladders
        self.factory.create_ladder(x=1, y=1, height=7)
        self.factory.create_ladder(x=8, y=1, height=5)

        self.create_food()

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_land_on_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor landed on a platform.
        """
        # search corresponding animation
        for sprite in self.factory.renderer.sprites:
            if sprite.actor == actor:
                action = animations.IDLE_ACTION
                delta_h = actor.fall_from_y - sprite.actor.y
                damage = get_falling_damage(delta_h)

                if delta_h > 1.5:
                    action = animations.LANDING_ACTION

                    # find character
                    relevant = [c for c in self.factory.characters if c.sprite.actor == actor]
                    if len(relevant) > 0:
                        c = relevant[0]
                        c.hit_points -= damage
                        if damage > 0:
                            # FIXME: on_player_wounded
                            animations.flash(sprite.animation, pygame.Color('white'))
                            if c.hit_points <= 0:
                                action = animations.DIE_ACTION

                animations.start(sprite.animation, action)
                return

    def on_falling(self, actor: platforms.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        pass

    def on_collide_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        pass

    def on_switch_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        pass

    def on_touch_actor(self, actor: platforms.Actor, other: platforms.Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        pass

    def on_reach_object(self, actor: platforms.Actor, obj: platforms.Object) -> None:
        """Triggered when the actor reaches an object.
        """
        # find character
        relevant = [c for c in self.factory.characters if c.sprite.actor == actor]
        if len(relevant) > 0:
            if obj.object_type == FOOD_OBJ:
                # heal him
                relevant[0].hit_points += 1
                # FIXME: on_player_healed
                self.create_food()

            elif obj.object_type == WEAPON_OBJ:
                # grab axe
                relevant[0].num_axes += 1
                # FIXME: on_weapon_collected

        self.factory.destroy_object(obj)

    def on_reach_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor reaches a ladder.
        """
        pass

    def on_leave_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor leaves a ladder.
        """
        pass

    # --- Animation Events -

    def on_step(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        pass

    def on_climb(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        pass

    def on_attack(self, ani: animations.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        pass

    def on_throw(self, ani: animations.Animation) -> None:
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
                                       y=sprite.actor.y + sprite.actor.radius, radius=platforms.OBJECT_RADIUS,
                                       face_x=sprite.actor.face_x, object_type=WEAPON_OBJ)

    def on_impact_platform(self, proj: platforms.Projectile, platform: platforms.Platform) -> None:
        """Triggered when a projectile hits a platform.
        """
        self.factory.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)

    def on_impact_actor(self, proj: platforms.Projectile, actor: platforms.Actor) -> None:
        """Triggered when a projectile hits an actor.
        """
        sprite = [sprite for sprite in self.factory.renderer.sprites if sprite.actor == actor][0]
        self.factory.destroy_sprite(sprite)
        self.factory.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)
