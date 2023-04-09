import pygame
import random
import math
from typing import Optional

from constants import *
import platforms
import animations
import factory


class Manager(platforms.PhysicsListener, animations.AnimationListener):

    def __init__(self):
        self.score = 0
        self.factory: Optional[factory.ObjectManager] = None

        self.player_sprite = None
        self.enemy_sprites = list()

    def create_food(self) -> None:
        # pick random position on random platform
        p = random.choice(self.factory.physics.platforms)
        x = random.randrange(p.width)

        self.factory.create_object(x=p.x + x, y=p.y + 0.5, object_type=FOOD_OBJ)

    def populate_demo_scene(self, guy_sheet: pygame.Surface) -> None:
        self.player_sprite = self.factory.create_actor_sprite(sprite_sheet=guy_sheet, x=2, y=5)
        self.enemy_sprites.append(self.factory.create_actor_sprite(sprite_sheet=guy_sheet, x=6.5, y=6.5))
        self.enemy_sprites.append(self.factory.create_actor_sprite(sprite_sheet=guy_sheet, x=6.5, y=4.5))

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

        for i in range(10):
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

                if delta_h > 2.5:
                    action = animations.LANDING_ACTION

                if delta_h > 4.0:
                    action = animations.DIE_ACTION

                animations.start(sprite.animation, action)
                return

    def on_falling(self, actor: platforms.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        print('falling')

    def on_collide_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        print('colliding')

    def on_switch_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        print('switching')

    def on_touch_actor(self, actor: platforms.Actor, other: platforms.Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        print('touched actor')

    def on_reach_object(self, actor: platforms.Actor, obj: platforms.Object) -> None:
        """Triggered when the actor reaches an object.
        """
        self.score += 1
        self.factory.destroy_object(obj)

        self.create_food()

    def on_reach_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor reaches a ladder.
        """
        print('reached ladder')

    def on_leave_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor leaves a ladder.
        """
        print('left ladder')

    # --- Animation Events -

    def on_step(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        print('step!')

    def on_climb(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        print('climb!')

    def on_attack(self, ani: animations.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        print('swing!')

    def on_throw(self, ani: animations.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        sprite = [sprite for sprite in self.factory.renderer.sprites if sprite.animation == ani][0]
        self.factory.create_projectile(origin=sprite.actor, x=sprite.actor.x,
                                       y=sprite.actor.y + sprite.actor.radius, radius=platforms.OBJECT_RADIUS,
                                       face_x=sprite.actor.face_x, object_type=WEAPON_OBJ)
        print('throw!')

    def on_impact_platform(self, proj: platforms.Projectile, platform: platforms.Platform) -> None:
        """Triggered when a projectile hits a platform.
        """
        self.factory.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)

    def on_impact_actor(self, proj: platforms.Projectile, actor: platforms.Actor) -> None:
        """Triggered when a projectile hits an actor.
        """
        sprite = [sprite for sprite in self.factory.renderer.sprites if sprite.actor == actor][0]
        self.factory.destroy_actor_sprite(sprite)
        self.factory.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.factory.destroy_projectile(proj)
