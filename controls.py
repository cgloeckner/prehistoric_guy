import pygame
from dataclasses import dataclass
from typing import Optional

import platforms
import tiles
import animations


NO_ACTION: int = 0
ATTACK_ACTION: int = 1
THROW_ACTION: int = 2


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
    def __init__(self, sprite: tiles.Sprite, binding: Keybinding):
        self.sprite = sprite
        self.binding = binding

        self.delta = pygame.math.Vector2()
        self.action = NO_ACTION

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
            print(self.attack_held_ms, THROW_THRESHOLD)
            if self.attack_held_ms > THROW_THRESHOLD:
                self.action = THROW_ACTION
            else:
                self.action = ATTACK_ACTION
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
                self.action = THROW_ACTION
                self.attack_held_ms = 0.0

    def handle_inputs(self) -> None:
        """Triggers movement, jumping, climbing, attacking etc.
        """
        if self.sprite.animation.action_id in [animations.DIE_ACTION, animations.ATTACK_ACTION,
                                               animations.THROW_ACTION, animations.LANDING_ACTION]:
            # nothing allowed
            self.sprite.actor.force_x = 0.0
            self.sprite.actor.force_y = 0.0
            return

        if self.action == THROW_ACTION:
            if self.sprite.animation.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            animations.start(self.sprite.animation, animations.THROW_ACTION)
            # FIXME: create projectile AFTER animation
            return

        if self.action == ATTACK_ACTION:
            if self.sprite.animation.action_id in [animations.HOLD_ACTION, animations.CLIMB_ACTION]:
                # not allowed
                return

            # attack!
            animations.start(self.sprite.animation, animations.ATTACK_ACTION)
            return

        if self.sprite.actor.ladder is None:
            # jumping?
            if self.delta.y > 0.0:
                # jump
                animations.start(self.sprite.animation, animations.JUMP_ACTION)
                self.sprite.actor.force_x = self.delta.x
                self.sprite.actor.force_y = self.delta.y
                return

            # moving?
            if self.delta.x != 0.0:
                # move around
                animations.start(self.sprite.animation, animations.MOVE_ACTION)
                self.sprite.actor.force_x = self.delta.x
                return

            # idle?
            if self.sprite.actor.force_y == 0.0:
                animations.start(self.sprite.animation, animations.IDLE_ACTION)
                self.sprite.actor.force_x = 0.0
                self.sprite.actor.force_y = 0.0

            return

        # jumping off?
        if self.delta.x != 0.0:
            # jump off ladder
            animations.start(self.sprite.animation, animations.JUMP_ACTION)
            self.sprite.actor.force_x = self.delta.x
            self.sprite.actor.force_y = self.delta.y
            return

        # climbing?
        if self.delta.y != 0.0:
            # climb on ladder
            animations.start(self.sprite.animation, animations.CLIMB_ACTION)
            self.sprite.actor.force_y = self.delta.y
            return

        self.sprite.actor.force_x = 0.0
        self.sprite.actor.force_y = 0.0

        # idle at top or bottom of the ladder?
        if platforms.within_ladder(self.sprite.actor):
            animations.start(self.sprite.animation, animations.HOLD_ACTION)
            return

        animations.start(self.sprite.animation, animations.IDLE_ACTION)

    def update(self, elapsed_ms: int) -> None:
        """Triggers movement/attack and animations.
        """
        self.get_inputs(elapsed_ms)
        self.handle_inputs()

        # reset all input parameters
        self.delta = pygame.math.Vector2()
        self.action = NO_ACTION
