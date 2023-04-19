import pygame
from dataclasses import dataclass, field
from typing import Optional
from enum import IntEnum

from core import constants
from platformer import physics, animations


# keypress time required to throw
THROW_THRESHOLD: int = int(constants.ANIMATION_NUM_FRAMES * animations.ANIMATION_FRAME_DURATION)


class Action(IntEnum):
    NONE = 0
    ATTACK = 1
    THROW = 2


@dataclass
class Keybinding:
    left_key: int = pygame.K_LEFT
    right_key: int = pygame.K_RIGHT
    up_key: int = pygame.K_UP
    down_key: int = pygame.K_DOWN
    attack_key: int = pygame.K_SPACE  # also for throwing


@dataclass
class InputState:
    """Combines input states.

    attack_held_ms describes for how long the attack key was held where -1 means it was not pressed recently.
    delta describes the intended movement vector.
    char_action describes the resulted Action (whether attack, throw or none).
    """

    attack_held_ms: int = -1
    delta: pygame.math.Vector2 = field(default_factory=pygame.math.Vector2)
    action: int = Action.NONE

    def reset(self):
        self.delta = pygame.math.Vector2()
        self.action = Action.NONE

    def process_event_action(self, binding: Keybinding, event: pygame.event.Event) -> None:
        """Handles inputs events and sets the action accordingly."""
        if event.type == pygame.KEYDOWN and event.key == binding.attack_key:
            self.attack_held_ms = 0
            return

        elif event.type == pygame.KEYUP and event.key == binding.attack_key:
            if self.attack_held_ms >= THROW_THRESHOLD:
                self.action = Action.THROW
            else:
                self.action = Action.ATTACK
            self.attack_held_ms = -1
            return

    def process_event_movement(self, binding: Keybinding, event: pygame.event.Event) -> None:
        """Handles input events and sets the movement vector accordinly."""
        if event.type == pygame.KEYDOWN:
            if event.key == binding.left_key:
                self.delta.x -= 1
            if event.key == binding.right_key:
                self.delta.x += 1
            if event.key == binding.up_key:
                self.delta.y += 1
            if event.key == binding.down_key:
                self.delta.y -= 1
        elif event.type == pygame.KEYUP:
            if event.key == binding.left_key:
                self.delta.x += 1
            if event.key == binding.right_key:
                self.delta.x -= 1
            if event.key == binding.up_key:
                self.delta.y -= 1
            if event.key == binding.down_key:
                self.delta.y += 1

    def get_throwing_progress(self) -> float:
        """Returns a float in [0.0; 1.0] that yields the percentage of the keydown-for-throwing duration."""
        if self.attack_held_ms == -1:
            return 0.0

        return min(1.0, self.attack_held_ms / THROW_THRESHOLD)

    def update(self, elapsed_ms: int) -> None:
        """Grabs the movement vector and whether it's an attack, throw or none."""
        # count how long the attack key is held
        if self.attack_held_ms >= 0:
            self.attack_held_ms += elapsed_ms
            if self.attack_held_ms >= THROW_THRESHOLD:
                self.action = Action.THROW
                self.attack_held_ms -= THROW_THRESHOLD

    def get_next_animation(self, is_on_ladder: bool, is_on_platform: bool) -> animations.Action:
        """Returns the related animation action or None if falling without an action-"""
        move_x = self.delta.x != 0.0
        move_y = self.delta.y != 0.0

        if self.action == Action.ATTACK:
            return animations.Action.ATTACK

        if self.action == Action.THROW:
            return animations.Action.THROW

        if move_x and move_y:
            return animations.Action.JUMP

        if is_on_ladder:
            if move_y:
                return animations.Action.CLIMB
            else:
                return animations.Action.HOLD

        if move_y:
            return animations.Action.JUMP

        if move_x:
            if is_on_platform:
                return animations.Action.MOVE
            else:
                return animations.Action.JUMP

        if is_on_platform:
            return animations.Action.IDLE
        else:
            return animations.Action.JUMP

    def verify_animation(self, phys_actor: physics.Actor, last_action: animations.Action,
                         next_action: animations.Action) -> Optional[animations.Action]:
        """Verifies the given action using physics and animation data.

        This checks whether the action is allowed or not (i.e. if it would interrupt an action that's meant to be not
        interruptable), prevents jumping with the toward key and also releases the ladder in case of jumping.
        """
        # stop if actor is in DYING or LANDING animations, which cannot be skipped
        if last_action in animations.BLOCKING_ANIMATIONS:
            return None

        # release ladder on case of jumping motion
        if self.delta.x != 0.0 and self.delta.y != 0:
            phys_actor.on_ladder = None

        # no jumping while jumping
        if last_action == next_action == animations.Action.JUMP:
            self.delta.y = 0.0

        return next_action
