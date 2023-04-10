import pygame
from dataclasses import dataclass
from typing import List, Optional

from core.constants import *
from core import resources
from core import ui

from platformer import animations
from platformer import physics
from platformer import render
from platformer import characters


# keypress time required to throw
THROW_THRESHOLD: int = int(animations.ANIMATION_NUM_FRAMES * animations.ANIMATION_FRAME_DURATION)


# HUD tileset columns
HEART_HUD: int = 0
WEAPON_HUD: int = 1


@dataclass
class Actor:
    object_id: int

    # key bindings
    left_key: int
    right_key: int
    up_key: int
    down_key: int
    attack_key: int  # also for throwing

    # time the attack key is held
    attack_held_ms: int = -1

    # movement vector
    delta_x: float = 0.0
    delta_y: float = 0.0

    char_action: int = characters.NO_ACTION


def get_throwing_process(player: Actor) -> float:
    """Returns a float in [0.0; 1.0] that yields the percentage of the keydown-for-throwing duration.
    """
    if player.attack_held_ms == -1:
        return 0.0

    return min(1.0, player.attack_held_ms / THROW_THRESHOLD)


class Players(object):
    def __init__(self, phys_system: physics.Physics, ani_system: animations.Animating, render_system: render.Renderer,
                 char_system: characters.Characters, cache: resources.Cache):
        self.phys_system = phys_system
        self.ani_system = ani_system
        self.render_system = render_system
        self.char_system = char_system

        self.players: List[Actor] = list()

        self.tileset = cache.get_image('hud')

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the actor who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.players if a.object_id == object_id][0]

    def try_get_by_id(self, object_id: int) -> Optional[Actor]:
        """Returns the actor who matches the given object_id or None
        """
        try:
            return self.get_by_id(object_id)
        except IndexError:
            return None

    def process_event(self, event: pygame.event.Event) -> None:
        """Handles inputs and sets the action accordingly.
        """
        for player in self.players:
            if event.type == pygame.KEYDOWN and event.key == player.attack_key:
                player.attack_held_ms = 0

            elif event.type == pygame.KEYUP and event.key == player.attack_key:
                if player.attack_held_ms > THROW_THRESHOLD:
                    player.char_action = characters.THROW_ACTION
                else:
                    player.char_action = characters.ATTACK_ACTION
                player.attack_held_ms = -1

    def get_inputs(self, player: Actor, elapsed_ms: int) -> None:
        """Grabs the movement vector and whether it's an attack or not.
        """
        keys = pygame.key.get_pressed()

        # query movement vector
        if keys[player.left_key]:
            player.delta_x -= 1
        if keys[player.right_key]:
            player.delta_x += 1
        if keys[player.up_key]:
            player.delta_y += 1
        if keys[player.down_key]:
            player.delta_y -= 1

        # count how long the attack key is held
        if player.attack_held_ms >= 0:
            player.attack_held_ms += elapsed_ms
            if player.attack_held_ms > THROW_THRESHOLD:
                player.char_action = characters.THROW_ACTION
                player.attack_held_ms = 0.0

    def handle_inputs(self, player: Actor) -> None:
        """Triggers movement, jumping, climbing, attacking etc.
        """
        ani_actor = self.ani_system.get_by_id(player.object_id)
        phys_actor = self.phys_system.get_by_id(player.object_id)

        if ani_actor.action_id in animations.BLOCKING_ANIMATIONS:
            # nothing allowed
            phys_actor.force_x = 0.0
            phys_actor.force_y = 0.0
            return

        if player.char_action == characters.THROW_ACTION:
            if ani_actor.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            animations.start(ani_actor, animations.THROW_ACTION)
            return

        if player.char_action == characters.ATTACK_ACTION:
            if ani_actor.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            # attack!
            animations.start(ani_actor, animations.ATTACK_ACTION)
            return

        if phys_actor.ladder is None:
            # jumping?
            if player.delta_y > 0.0:
                # jump
                animations.start(ani_actor, animations.JUMP_ACTION)
                phys_actor.force_x = player.delta_x
                phys_actor.force_y = player.delta_y
                return
            # moving?
            if player.delta_x != 0.0:
                # move around
                animations.start(ani_actor, animations.MOVE_ACTION)
                phys_actor.force_x = player.delta_x
                return

            # idle?
            if phys_actor.force_y == 0.0:
                animations.start(ani_actor, animations.IDLE_ACTION)
                phys_actor.force_x = 0.0
                phys_actor.force_y = 0.0

            return

        # jumping off?
        if player.delta_x != 0.0:
            # jump off ladder
            animations.start(ani_actor, animations.JUMP_ACTION)
            phys_actor.force_x = player.delta_x
            phys_actor.force_y = player.delta_y
            return

        # climbing?
        if player.delta_y != 0.0:
            # climb on ladder
            animations.start(ani_actor, animations.CLIMB_ACTION)
            phys_actor.force_y = player.delta_y
            return

        phys_actor.force_x = 0.0
        phys_actor.force_y = 0.0

        # idle at top or bottom of the ladder?
        if physics.within_ladder(phys_actor):
            animations.start(ani_actor, animations.HOLD_ACTION)
            return

        animations.start(ani_actor, animations.IDLE_ACTION)

    def update(self, elapsed_ms: int) -> None:
        """Triggers movement/attack and animations.
        """
        for player in self.players:
            self.get_inputs(player, elapsed_ms)
            self.handle_inputs(player)

            # reset all input parameters
            player.delta_x = 0
            player.delta_y = 0
            player.char_action = characters.NO_ACTION

    def draw_icons(self, char_actor: characters.Actor) -> None:
        for i in range(char_actor.hit_points):
            self.render_system.target.blit(self.tileset, (i * OBJECT_SCALE, 0),
                                           (0 * OBJECT_SCALE, HEART_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))

        for i in range(char_actor.num_axes):
            self.render_system.target.blit(self.tileset, (i * OBJECT_SCALE, OBJECT_SCALE),
                                           (0 * OBJECT_SCALE, WEAPON_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))

    def draw_throw_progress(self, char_actor: characters.Actor, value: float) -> None:
        phys_actor = self.phys_system.get_by_id(char_actor.object_id)

        pos = self.render_system.world_to_screen_coord(phys_actor.x, phys_actor.y)
        pos.y -= WORLD_SCALE

        ui.progress_bar(self.render_system.target, pos.x, pos.y, 15, 3, value)

    def draw(self) -> None:
        for player in self.players:
            char_actor = self.char_system.try_get_by_id(player.object_id)
            if char_actor is None:
                continue

            self.draw_icons(char_actor)

            # FIXME: hide progress when not allowed to perform throwing (e.g. during jump)
            value = get_throwing_process(player)
            if value > 0.0:
                self.draw_throw_progress(char_actor, value)
