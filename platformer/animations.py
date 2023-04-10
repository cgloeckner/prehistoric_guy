import pygame
import math
from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional, List

from core.constants import *
from core import resources


ANIMATION_FRAME_DURATION: int = 120

MOVEMENT_SWING: float = 1.0
CLIMB_SWING: float = 7.0

IDLE_ACTION: int = 0
MOVE_ACTION: int = 1
HOLD_ACTION: int = 2
CLIMB_ACTION: int = 3
ATTACK_ACTION: int = 4
THROW_ACTION: int = 5
JUMP_ACTION: int = 6
LANDING_ACTION: int = 7
DIE_ACTION: int = 8

# animations that cannot be interrupted by user input
BLOCKING_ANIMATIONS = [DIE_ACTION, ATTACK_ACTION, THROW_ACTION, LANDING_ACTION]

# those loop until interrupted by user input
LOOPED_ANIMATIONS = [IDLE_ACTION, MOVE_ACTION, HOLD_ACTION]

# those animations lead to IDLE when finished
RESET_TO_IDLE_ANIMATIONS = [ATTACK_ACTION, THROW_ACTION, LANDING_ACTION]

@dataclass
class Actor:
    object_id: int

    # frame animation: row and column index, animation delay until frame is switched
    action_id: int = 0
    frame_id: int = 0
    frame_duration_ms: int = ANIMATION_FRAME_DURATION
    frame_max_duration_ms: int = ANIMATION_FRAME_DURATION
    # movement animation
    delta_y: float = 0.0
    total_frame_time_ms: int = 0
    # hsl animation
    hsl: Optional[resources.HslTransform] = None
    hsl_duration_ms: int = ANIMATION_FRAME_DURATION


def start(ani: Actor, action_id: int, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the frame animation with the given action.
    """
    if ani.action_id == action_id:
        return

    ani.action_id = action_id
    ani.frame_id = 0
    ani.frame_duration_ms = duration_ms
    ani.frame_max_duration_ms = duration_ms
    ani.total_frame_time_ms = 0


def flash(ani: Actor, hsl: resources.HslTransform, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the color animation with the given color.
    """
    ani.hsl = hsl
    ani.hsl_duration_ms = duration_ms


class AnimationListener(object):

    @abstractmethod
    def on_step(self, ani: Actor) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        pass

    @abstractmethod
    def on_climb(self, ani: Actor) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        pass

    @abstractmethod
    def on_attack(self, ani: Actor) -> None:
        """Triggered when an attack animation finished.
        """
        pass

    @abstractmethod
    def on_throw(self, ani: Actor) -> None:
        """Triggered when a throwing animation finished.
        """
        pass

    @abstractmethod
    def on_died(self, ani: Actor) -> None:
        """Triggered when a dying animation finished.
        """
        pass


class Animating(object):
    """Handles all frame set animations.
    """
    def __init__(self, animation_listener: AnimationListener):
        self.animations: List[Actor] = list()
        self.event_listener = animation_listener

    def get_by_id(self, object_id: int) -> Actor:
        """Returns the animation who matches the given object_id.
        May throw an IndexError.
        """
        return [a for a in self.animations if a.object_id == object_id][0]

    def notify_animation(self, ani: Actor) -> None:
        """Notify about a finished animation.
        """
        if ani.action_id == MOVE_ACTION:
            self.event_listener.on_step(ani)
        elif ani.action_id == ATTACK_ACTION:
            self.event_listener.on_attack(ani)
        elif ani.action_id == THROW_ACTION:
            self.event_listener.on_throw(ani)

    def update_frame(self, ani: Actor, elapsed_ms: int) -> None:
        """Update a single frame animation.
        """
        # continue animation
        ani.frame_duration_ms -= elapsed_ms
        if ani.frame_duration_ms > 0:
            return

        ani.frame_duration_ms += ani.frame_max_duration_ms
        ani.frame_id += 1

        if ani.frame_id < ANIMATION_NUM_FRAMES:
            return

        # handle animation type (loop, reset, freeze)
        self.notify_animation(ani)

        if ani.action_id in LOOPED_ANIMATIONS:
            # loop
            ani.frame_id = 0
        elif ani.action_id in RESET_TO_IDLE_ANIMATIONS:
            # reset to idle
            ani.frame_id = 0
            ani.action_id = IDLE_ACTION
        elif ani.action_id == CLIMB_ACTION:
            # reset to hold
            ani.frame_id = 0
            ani.action_id = HOLD_ACTION
        else:
            # freeze at last frame
            ani.frame_id -= 1

    def update_hsl(self, ani: Actor, elapsed_ms: int) -> None:
        if ani.hsl is None:
            return

        ani.hsl_duration_ms -= elapsed_ms
        if ani.hsl_duration_ms > 0:
            return

        ani.hsl_duration_ms = 0
        ani.hsl = None

    def update_movement(self, ani: Actor, elapsed_ms: int) -> None:
        """Updates the movement animation, where a small height difference is applied while moving and climbing.
        """
        if ani.action_id not in [MOVE_ACTION, CLIMB_ACTION]:
            ani.total_frame_time_ms = 0
            return

        ani.total_frame_time_ms += elapsed_ms
        if ani.action_id == MOVE_ACTION:
            # |sin(x)|
            angle = 2 * math.pi * ani.total_frame_time_ms / 360
            ani.delta_y = MOVEMENT_SWING * math.sin(angle / MOVEMENT_SWING)
        else:
            # sawtooth
            value = ani.total_frame_time_ms / 1000.0
            ani.delta_y = CLIMB_SWING * (value - int(value))

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for ani in self.animations:
            self.update_frame(ani, elapsed_ms)
            self.update_hsl(ani, elapsed_ms)
            self.update_movement(ani, elapsed_ms)


def main():
    from core.constants import SPRITE_SCALE
    from core import resources

    class DemoListener(AnimationListener):
        def on_step(self, a: Actor) -> None:
            pass

        def on_climb(self, a: Actor) -> None:
            pass

        def on_attack(self, a: Actor) -> None:
            pass

        def on_throw(self, a: Actor) -> None:
            pass

        def on_died(self, a: Actor) -> None:
            pass

    pygame.init()

    # get native resolution and factor for scaling
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= SPRITE_SCALE
    native_height //= SPRITE_SCALE
    ui_scale_factor = max(1, min(native_width, native_height))
    ui_scale_factor //= 4

    # calculate window resolution and initialize screen
    window_width = SPRITE_SCALE * ui_scale_factor
    window_height = SPRITE_SCALE * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height))
    buffer = pygame.Surface((SPRITE_SCALE, SPRITE_SCALE))
    clock = pygame.time.Clock()

    cache = resources.Cache('../data')
    guy = cache.get_sprite_sheet('guy')
    guy = cache.get_hsl_transformed(guy, resources.HslTransform(hue=0.2), SPRITE_CLOTHES_COLORS)
    look_right = True

    listener = DemoListener()
    ani = Animating(listener)
    ani.animations.append(Actor(1))

    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            look_right = False
        if keys[pygame.K_d]:
            look_right = True
        if keys[pygame.K_1]:
            start(ani.animations[0], IDLE_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_2]:
            start(ani.animations[0], MOVE_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_3]:
            start(ani.animations[0], HOLD_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_4]:
            start(ani.animations[0], CLIMB_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_5]:
            start(ani.animations[0], ATTACK_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_6]:
            start(ani.animations[0], THROW_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_7]:
            start(ani.animations[0], JUMP_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_8]:
            start(ani.animations[0], LANDING_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_9]:
            start(ani.animations[0], DIE_ACTION, ANIMATION_FRAME_DURATION)

        ani.update(elapsed)

        buffer.fill('lightblue')
        x_offset = (0 if look_right else 1) * ANIMATION_NUM_FRAMES * SPRITE_SCALE
        rect = pygame.Rect(ani.animations[0].frame_id * SPRITE_SCALE + x_offset,
                           ani.animations[0].action_id * SPRITE_SCALE, SPRITE_SCALE, SPRITE_SCALE)
        buffer.blit(guy, (0, -ani.animations[0].delta_y), rect)
        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
