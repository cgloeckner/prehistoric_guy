import pygame
from dataclasses import dataclass
from typing import Tuple

import platforms
import tiles
import animations


@dataclass
class Keybinding:
    left: int
    right: int
    up: int
    down: int
    attack: int


class Player(object):
    def __init__(self, sprite: tiles.Sprite, binding: Keybinding):
        self.sprite = sprite
        self.binding = binding

    def get_inputs(self) -> Tuple[pygame.math.Vector2, bool]:
        """Grabs the movement vector and whether it's an attack or not.
        Returns the vector and the bool.
        """
        keys = pygame.key.get_pressed()

        # query movement vector
        delta = pygame.math.Vector2()
        if keys[self.binding.left]:
            delta.x -= 1
        if keys[self.binding.right]:
            delta.x += 1
        if keys[self.binding.up]:
            delta.y += 1
        if keys[self.binding.down]:
            delta.y -= 1

        attack = keys[self.binding.attack]

        return delta, attack

    def update(self) -> None:
        """Triggers movement/attack and animations.
        """
        delta, attack = self.get_inputs()

        if self.sprite.animation.action_id in [animations.DIE_ACTION, animations.ATTACK_ACTION,
                                               animations.LANDING_ACTION]:
            # nothing allowed
            self.sprite.actor.force_x = 0.0
            self.sprite.actor.force_y = 0.0
            return

        if attack:
            # attack!
            animations.start(self.sprite.animation, animations.ATTACK_ACTION)
            return

        if self.sprite.actor.ladder is None:
            # jumping?
            if delta.y > 0.0:
                # jump
                animations.start(self.sprite.animation, animations.JUMP_ACTION)
                self.sprite.actor.force_x = delta.x
                self.sprite.actor.force_y = delta.y
                return

            # moving?
            if delta.x != 0.0:
                # move around
                animations.start(self.sprite.animation, animations.MOVE_ACTION)
                self.sprite.actor.force_x = delta.x
                return

            # idle?
            if self.sprite.actor.force_y == 0.0:
                animations.start(self.sprite.animation, animations.IDLE_ACTION)
                self.sprite.actor.force_x = 0.0
                self.sprite.actor.force_y = 0.0

            return

        # jumping off?
        if delta.x != 0.0:
            # jump off ladder
            animations.start(self.sprite.animation, animations.JUMP_ACTION)
            self.sprite.actor.force_x = delta.x
            self.sprite.actor.force_y = delta.y
            return

        # climbing?
        if delta.y != 0.0:
            # climb on ladder
            animations.start(self.sprite.animation, animations.CLIMB_ACTION)
            self.sprite.actor.force_y = delta.y
            return

        self.sprite.actor.force_x = 0.0
        self.sprite.actor.force_y = 0.0

        # idle at top or bottom of the ladder?
        if platforms.within_ladder(self.sprite.actor):
            animations.start(self.sprite.animation, animations.HOLD_ACTION)
            return

        animations.start(self.sprite.animation, animations.IDLE_ACTION)
