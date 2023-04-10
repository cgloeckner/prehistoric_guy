import pygame
from dataclasses import dataclass

import platformer.animations as animations
import platformer.physics as physics
import platformer.characters as characters


# keypress time required to throw
THROW_THRESHOLD: int = int(animations.ANIMATION_NUM_FRAMES * animations.ANIMATION_FRAME_DURATION)


@dataclass
class Keybinding:
    left: int
    right: int
    up: int
    down: int
    # for both, attack and throw
    attack: int


class Player(object):
    def __init__(self, phys_actor: physics.Actor, ani_actor: animations.Actor, binding: Keybinding):
        self.phys_actor = phys_actor
        self.ani_actor = ani_actor
        self.binding = binding

        self.delta = pygame.math.Vector2()
        self.action = characters.NO_ACTION

        self.attack_held_ms = -1

    def get_throwing_process(self) -> float:
        """Returns a float in [0.0; 1.0] that yields the percentage of the keydown-for-throwing duration.
        """
        if self.attack_held_ms == -1:
            return 0.0

        return min(1.0, self.attack_held_ms / THROW_THRESHOLD)

    def process_event(self, event: pygame.event.Event) -> None:
        """Handles inputs and sets the action accordingly.
        """
        if event.type == pygame.KEYDOWN and event.key == self.binding.attack:
            self.attack_held_ms = 0

        elif event.type == pygame.KEYUP and event.key == self.binding.attack:
            if self.attack_held_ms > THROW_THRESHOLD:
                self.action = characters.THROW_ACTION
            else:
                self.action = characters.ATTACK_ACTION
            self.attack_held_ms = -1

    def get_inputs(self, elapsed_ms: int) -> None:
        """Grabs the movement vector and whether it's an attack or not.
        """
        keys = pygame.key.get_pressed()

        # query movement vector
        if keys[self.binding.left]:
            self.delta.x -= 1
        if keys[self.binding.right]:
            self.delta.x += 1
        if keys[self.binding.up]:
            self.delta.y += 1
        if keys[self.binding.down]:
            self.delta.y -= 1

        # count how long the attack key is held
        if self.attack_held_ms >= 0:
            self.attack_held_ms += elapsed_ms
            if self.attack_held_ms > THROW_THRESHOLD:
                self.action = characters.THROW_ACTION
                self.attack_held_ms = 0.0

    def handle_inputs(self) -> None:
        """Triggers movement, jumping, climbing, attacking etc.
        """
        if self.ani_actor.action_id in [animations.DIE_ACTION, animations.ATTACK_ACTION,
                                        animations.THROW_ACTION, animations.LANDING_ACTION]:
            # nothing allowed
            self.phys_actor.force_x = 0.0
            self.phys_actor.force_y = 0.0
            return

        if self.action == characters.THROW_ACTION:
            if self.ani_actor.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            animations.start(self.ani_actor, animations.THROW_ACTION)
            # FIXME: create projectile AFTER animation
            return

        if self.action == characters.ATTACK_ACTION:
            if self.ani_actor.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            # attack!
            animations.start(self.ani_actor, animations.ATTACK_ACTION)
            return

        if self.phys_actor.ladder is None:
            # jumping?
            if self.delta.y > 0.0:
                # jump
                animations.start(self.ani_actor, animations.JUMP_ACTION)
                self.phys_actor.force_x = self.delta.x
                self.phys_actor.force_y = self.delta.y
                return

            # moving?
            if self.delta.x != 0.0:
                # move around
                animations.start(self.ani_actor, animations.MOVE_ACTION)
                self.phys_actor.force_x = self.delta.x
                return

            # idle?
            if self.phys_actor.force_y == 0.0:
                animations.start(self.ani_actor, animations.IDLE_ACTION)
                self.phys_actor.force_x = 0.0
                self.phys_actor.force_y = 0.0

            return

        # jumping off?
        if self.delta.x != 0.0:
            # jump off ladder
            animations.start(self.ani_actor, animations.JUMP_ACTION)
            self.phys_actor.force_x = self.delta.x
            self.phys_actor.force_y = self.delta.y
            return

        # climbing?
        if self.delta.y != 0.0:
            # climb on ladder
            animations.start(self.ani_actor, animations.CLIMB_ACTION)
            self.phys_actor.force_y = self.delta.y
            return

        self.phys_actor.force_x = 0.0
        self.phys_actor.force_y = 0.0

        # idle at top or bottom of the ladder?
        if physics.within_ladder(self.phys_actor):
            animations.start(self.ani_actor, animations.HOLD_ACTION)
            return

        animations.start(self.ani_actor, animations.IDLE_ACTION)

    def update(self, elapsed_ms: int) -> None:
        """Triggers movement/attack and animations.
        """
        self.get_inputs(elapsed_ms)
        self.handle_inputs()

        # reset all input parameters
        self.delta = pygame.math.Vector2()
        self.action = characters.NO_ACTION
