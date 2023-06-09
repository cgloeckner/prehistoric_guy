import pygame
import math
from typing import Optional

from core import constants, resources, state_machine

from platformer import animations, characters, controls, physics, editor
from platformer import factory


class GameState(state_machine.State, factory.EventListener):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = resources.Cache(engine.paths)

        # --- loading some resources ----------------------------------------------------------------------------------
        self.font = self.cache.get_font()
        guy_path = self.engine.paths.sprite('guy')
        player_guy = self.cache.get_sprite_sheet(guy_path)
        # --- setup object manager with player character ---------------------------------------------------------------
        self.factory = factory.Factory(self, self.cache, engine.buffer)
        self.engine.fill_color = self.factory.parallax.get_fill_color()

        level_files = editor.get_level_files(self.engine.paths.level())
        filename = self.engine.paths.level(level_files[0])
        editor.load_level(filename, self.factory.ctx.physics)

        pos = pygame.math.Vector2(5, 5)
        player_char_actor = self.factory.create_character(sprite_sheet=player_guy, x=pos.x, y=pos.y, max_hit_points=5,
                                                          num_axes=10)
        self.factory.create_player(player_char_actor,
                                   keys=controls.Keybinding(left_key=pygame.K_a, right_key=pygame.K_d,
                                                            up_key=pygame.K_w, down_key=pygame.K_s,
                                                            attack_key=pygame.K_SPACE))

        self.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)

        # --- create demo scene ---------------------------------------------------------------------------------------
        for value, color_set in enumerate([constants.SNOW_CLOTHES_COLORS, constants.GRASS_CLOTHES_COLOR,
                                           constants.STONE_CLOTHES_COLOR, constants.EMBER_CLOTHES_COLOR]):
            enemy_guy = player_guy.copy()
            resources.transform_color_replace(enemy_guy, dict(zip(constants.SPRITE_CLOTHES_COLORS, color_set)))
            self.factory.create_enemy(sprite_sheet=enemy_guy, x=6.25 + value, y=5.5, max_hit_points=3, num_axes=0)
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

        if proj in self.factory.ctx.physics.projectiles:
            self.factory.ctx.physics.projectiles.remove(proj)

    def on_touch_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        """Triggered when an actor touches another actor."""
        pass

    # ------------------------------------------------------------------------------------------------------------------
    # --- Animation Events -

    def on_animation_finish(self, ani: animations.Actor) -> None:
        """Triggered when an attack animation finished."""
        actor = self.factory.ctx.characters.actors.get_by_id(ani.object_id)
        if actor is None:
            return

        if ani.frame.action == animations.Action.ATTACK:
            victims = characters.query_melee_range(actor, self.factory.ctx.characters, self.factory.ctx.physics)
            for victim in victims:
                characters.attack_enemy(1, victim)
                self.on_char_damaged(victim, 1, actor)

        elif ani.frame.action == animations.Action.THROW:
            actor = self.factory.ctx.characters.actors.get_by_id(ani.object_id)
            proj = characters.throw_object(actor, 3.0, constants.ObjectType.WEAPON, self.factory.ctx.physics,
                                           self.factory.create_projectile)
            if proj is not None:
                proj.move.force.y = 1.0

    # ------------------------------------------------------------------------------------------------------------------
    # --- Character events

    def on_char_damaged(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        """Triggered when an actor got damaged."""
        if char_actor.hit_points > 0:
            return

        ani_actor = self.factory.ctx.animations.actors.get_by_id(char_actor.object_id)
        ani_actor.frame.start(animations.Action.DIE)

        phys_actor = self.factory.ctx.physics.actors.get_by_id(char_actor.object_id)
        phys_actor.move.force.x = 0.0
        phys_actor.can_collide = False

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

    def update(self, elapsed_ms: int) -> None:
        # --- Demo Camera movement -------------------------------------------------------------------------------------
        player_char_actor = self.factory.ctx.players.actors[0]
        phys_actor = self.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)
        self.factory.camera.set_center_x(phys_actor.pos.x)

        self.factory.update(elapsed_ms)

        # --- Demo: limit pos to screen --------------------------------------------------------------------------------
        for player in self.factory.ctx.players.actors:
            phys_actor = self.factory.ctx.physics.actors.get_by_id(player.object_id)
            if phys_actor.pos.y < -10:
                self.engine.pop()

    def draw(self) -> None:
        self.factory.draw()

        # draw FPS
        size = list(pygame.display.get_window_size())
        if constants.SCALE_2X:
            size[1] //= 2
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, size[1] - fps_surface.get_height()))
