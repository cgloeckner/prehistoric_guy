import pygame
import math
from typing import Optional

from core import constants, resources, state_machine

from platformer import animations, characters
from platformer import factory
from platformer import controls, physics


class GameState(state_machine.State, factory.EventListener):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = resources.Cache()

        # --- loading some resources ----------------------------------------------------------------------------------
        self.font = self.cache.get_font()
        generic_guy = self.cache.get_sprite_sheet('guy')
        blue_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(hue=216),
                                                  constants.SPRITE_CLOTHES_COLORS)
        grey_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(saturation=0),
                                                  constants.SPRITE_CLOTHES_COLORS)

        # --- setup object manager with player character ---------------------------------------------------------------
        self.factory = factory.Factory(self, self.cache, engine.buffer)
        player_char_actor = self.factory.create_character(sprite_sheet=blue_guy, x=2, y=5, max_hit_points=5,
                                                          num_axes=10)
        self.factory.create_player(player_char_actor,
                                   keys=controls.Keybinding(left_key=pygame.K_a, right_key=pygame.K_d,
                                                            up_key=pygame.K_w, down_key=pygame.K_s,
                                                            attack_key=pygame.K_SPACE))

        self.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)

        # --- create demo scene ---------------------------------------------------------------------------------------
        self.factory.create_enemy(sprite_sheet=grey_guy, x=6.5, y=6.5, max_hit_points=2, num_axes=0)
        self.factory.create_enemy(sprite_sheet=grey_guy, x=6.5, y=4.5, max_hit_points=2, num_axes=0)

        # horizontal platforms
        self.factory.ctx.physics.create_platform(x=1, y=1, width=3, height=1)
        self.factory.ctx.physics.create_platform(x=1, y=6, width=3)
        self.factory.ctx.physics.create_platform(x=7, y=2, width=3, height=2)
        self.factory.ctx.physics.create_platform(x=2, y=2, width=2)
        self.factory.ctx.physics.create_platform(x=0, y=4, width=3)
        self.factory.ctx.physics.create_platform(x=6, y=1, width=3)
        for i in range(10):
            self.factory.ctx.physics.create_platform(x=10 + i, y=0, width=1, height=1 + i)
        self.factory.ctx.physics.create_platform(x=5, y=6, width=4)

        self.factory.ctx.physics.create_platform(x=3, y=7, width=1, hover=physics.Hovering(x=math.cos, amplitude=-2))

        self.factory.ctx.physics.create_platform(x=1, y=11, width=12)

        self.factory.create_random_object()
        self.factory.ctx.physics.create_object(x=1, y=1, object_type=constants.ObjectType.FOOD)

        self.factory.ctx.physics.create_platform(x=-12, y=0, width=15)
        self.factory.ctx.physics.create_platform(x=-8, y=1, width=5, height=5)
        self.factory.ctx.physics.create_platform(x=-12, y=0, width=3, height=10)

        # ladders
        self.factory.ctx.physics.create_ladder(x=1.5, y=2, height=4)
        self.factory.ctx.physics.create_ladder(x=8.5, y=1, height=5)
        self.factory.ctx.physics.create_ladder(x=2.5, y=6, height=5)

    # ------------------------------------------------------------------------------------------------------------------
    # --- physics events ---

    def on_grab(self, actor: physics.Actor) -> None:
        """Triggered when the actor grabs a ladder."""
        player = self.factory.ctx.players.actors.get_by_id(actor.object_id)
        if player is not None:
            return

        # enemy! let 'm climb
        actor.pos.x = actor.on_ladder.pos.x
        actor.move.force.x = 0.0
        actor.move.force.y = 0.0
        ani_enemy = self.factory.ctx.animations.actors.get_by_id(actor.object_id)
        ani_enemy.frame.start(animations.Action.IDLE)

    def on_release(self, actor: physics.Actor) -> None:
        """Triggered when the actor releases a ladder."""
        pass

    def on_falling(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor starts falling."""
        actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        characters.set_falling_from(actor, phys_actor)

    def on_landing(self, phys_actor: physics.Actor) -> None:
        """Triggered when the actor landed on a platform."""
        actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        action, damage = characters.apply_landing(actor, phys_actor)
        ani_actor = self.factory.ctx.animations.actors.get_by_id(phys_actor.object_id)

        if damage > 0:
            if actor.hit_points == 0:
                self.on_char_died(actor, damage, None)
            else:
                self.on_char_damaged(actor, damage, None)

        else:
            ani_actor.frame.start(action)

    def on_collision(self, actor: physics.Actor, platform: physics.Platform) -> None:
        """Triggered when the actor runs into a platform."""
        pass

    def on_touch_object(self, phys_actor: physics.Actor, obj: physics.Object) -> None:
        """Triggered when the actor reaches an object."""
        char_actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            if obj.object_type == constants.ObjectType.FOOD:
                # heal him
                char_actor.hit_points += 1
                # FIXME: on_player_healed

            elif obj.object_type == constants.ObjectType.WEAPON:
                # grab axe
                char_actor.num_axes += 1
                # FIXME: on_weapon_collected

        self.factory.ctx.physics.objects.remove(obj)
        self.factory.create_random_object()

    def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
        """Triggered when a projectile hits a platform."""
        self.factory.ctx.physics.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                               object_type=proj.object_type)
        self.factory.ctx.physics.projectiles.remove(proj)

    def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when a projectile hits an actor."""
        char_actor = self.factory.ctx.characters.actors.get_by_id(phys_actor.object_id)
        if char_actor is not None:
            self.factory.characters.apply_projectile_hit(char_actor, 2, proj)

        # drop projectile as object
        self.factory.ctx.physics.create_object(x=proj.pos.x, y=proj.pos.y - constants.OBJECT_RADIUS,
                                               object_type=proj.object_type)

        self.factory.ctx.physics.projectiles.remove(proj)

    def on_touch_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when an actor touches another actor."""
        pass

    # ------------------------------------------------------------------------------------------------------------------
    # --- Animation Events -

    def on_climb(self, ani: animations.Actor) -> None:
        pass

    def on_step(self, ani: animations.Actor) -> None:
        pass

    def on_attack(self, ani: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.factory.ctx.characters.actors.get_by_id(ani.object_id)
        if actor is None:
            return

        victims = characters.query_melee_range(actor, self.factory.ctx.characters, self.factory.ctx.physics)
        for victim in victims:
            characters.attack_enemy(1, victim)
            if victim.hit_points == 0:
                self.on_char_died(victim, 1, actor)
            else:
                self.on_char_damaged(victim, 1, actor)

    def on_throw(self, ani_actor: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.factory.ctx.characters.actors.get_by_id(ani_actor.object_id)
        proj = characters.throw_object(actor, 3.0, constants.ObjectType.WEAPON, self.factory.ctx.physics,
                                       self.factory.create_projectile)
        proj.move.force.y = 1.0

    def on_died(self, ani_actor: animations.Actor) -> None:
        """Triggered when a dying animation finished."""
        pass

    # ------------------------------------------------------------------------------------------------------------------
    # --- Character events

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor got damaged."""
        pass

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor died. An optional cause can be provided."""
        ani_actor = self.factory.ctx.animations.actors.get_by_id(char_actor.object_id)
        ani_actor.frame.start(animations.Action.DIE)

        phys_actor = self.factory.ctx.physics.actors.get_by_id(char_actor.object_id)
        phys_actor.force_x = 0.0
        phys_actor.can_collide = False

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.factory.players.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        # --- Demo Camera movement -------------------------------------------------------------------------------------
        player_char_actor = self.factory.ctx.players.actors[0]
        phys_actor = self.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)
        self.factory.camera.set_center(phys_actor.pos, constants.WORLD_SCALE)

        self.factory.update(elapsed_ms)

        # --- Demo: limit pos to screen --------------------------------------------------------------------------------
        for player in self.factory.ctx.players.actors:
            phys_actor = self.factory.ctx.physics.actors.get_by_id(player.object_id)
            if phys_actor.pos.y < 0:
                phys_actor.pos.y += constants.RESOLUTION_Y // constants.WORLD_SCALE

    def draw(self) -> None:
        self.factory.draw()

        # draw FPS
        size = self.engine.get_pygame_size()
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, size[1] - fps_surface.get_height()))
