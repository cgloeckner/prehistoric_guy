import pygame
from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional

from constants import ANIMATION_NUM_FRAMES


ANIMATION_FRAME_DURATION: int = 100

IDLE_ACTION: int = 0
MOVE_ACTION: int = 1
HOLD_ACTION: int = 2
CLIMB_ACTION: int = 3
ATTACK_ACTION: int = 4
JUMP_ACTION: int = 5
LANDING_ACTION: int = 6
DIE_ACTION: int = 7


@dataclass
class Animation:
    id: int
    # frame animation: row and column index, animation delay until frame is switched
    action_id: int = 0
    frame_id: int = 0
    frame_duration_ms: int = ANIMATION_FRAME_DURATION
    frame_max_duration_ms: int = ANIMATION_FRAME_DURATION
    # color animation
    color: Optional[pygame.Color] = None
    color_duration_ms: int = ANIMATION_FRAME_DURATION


def flip_sprite_sheet(src: pygame.Surface, tile_size: int) -> pygame.Surface:
    """Splits all sprite frames but keeps the logical order of the entire sprite sheet.
    A new sprite sheet is returned which holds all sprites (left: original, right: flipped frames).
    """
    size = src.get_size()
    mirr = pygame.transform.flip(src, flip_x=True, flip_y=False)
    dst = pygame.Surface((size[0] * 2, size[1]), flags=pygame.SRCALPHA)

    dst.blit(src, (0, 0))
    for column in range(src.get_width() // tile_size):
        dst.blit(mirr, (size[0] + column * tile_size, 0), (size[0] - (column + 1) * tile_size, 0, tile_size, size[1]))

    return dst


def start(ani: Animation, action_id: int, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the frame animation with the given action.
    """
    if ani.action_id == action_id:
        return

    ani.action_id = action_id
    ani.frame_id = 0
    ani.frame_duration_ms = duration_ms
    ani.frame_max_duration_ms = duration_ms


def flash(ani: Animation, color: pygame.Color, duration_ms: int = ANIMATION_FRAME_DURATION) -> None:
    """Resets the color animation with the given color.
    """
    ani.color = color
    ani.color_duration_ms = duration_ms


class AnimationListener(object):

    @abstractmethod
    def on_step(self, ani: Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        pass

    @abstractmethod
    def on_climb(self, ani: Animation) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        pass

    @abstractmethod
    def on_attack(self, ani: Animation) -> None:
        """Triggered when an attack animation finished.
        """
        pass


class Animating(object):
    """Handles all frame set animations.
    """
    def __init__(self, animation_listener: AnimationListener):
        self.animations = list()
        self.event_listener = animation_listener

    def notify_animation(self, ani: Animation) -> None:
        """Notify about a finished animation.
        """
        if ani.action_id == MOVE_ACTION:
            self.event_listener.on_step(ani)
        elif ani.action_id == ATTACK_ACTION:
            self.event_listener.on_attack(ani)

    def update_frame(self, ani: Animation, elapsed_ms: int) -> None:
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

        if ani.action_id in [IDLE_ACTION, MOVE_ACTION, HOLD_ACTION]:
            # loop
            ani.frame_id = 0
        elif ani.action_id in [ATTACK_ACTION, LANDING_ACTION]:
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

    def update_color(self, ani: Animation, elapsed_ms: int) -> None:
        if ani.color is None:
            return

        ani.color_duration_ms -= elapsed_ms
        if ani.color_duration_ms > 0:
            return

        ani.color_duration_ms = 0
        ani.color = None

        # FIXME: trigger event using self.on_flashed?

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for ani in self.animations:
            self.update_frame(ani, elapsed_ms)
            self.update_color(ani, elapsed_ms)


def main():
    from constants import SPRITE_SCALE

    class DemoListener(AnimationListener):
        def on_step(self, a: Animation) -> None:
            print(f'{a} steps')

        def on_attack(self, a: Animation) -> None:
            print(f'{a} finished attack')

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

    guy = pygame.image.load('data/guy.png')
    guy = flip_sprite_sheet(guy, SPRITE_SCALE)
    look_right = True

    listener = DemoListener()
    ani = Animating(listener)
    ani.frame_animations.append(Animation(1))

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
            start(ani.frame_animations[0], IDLE_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_2]:
            start(ani.frame_animations[0], MOVE_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_3]:
            start(ani.frame_animations[0], ATTACK_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_4]:
            start(ani.frame_animations[0], JUMP_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_5]:
            start(ani.frame_animations[0], LANDING_ACTION, ANIMATION_FRAME_DURATION)
        if keys[pygame.K_6]:
            start(ani.frame_animations[0], DIE_ACTION, ANIMATION_FRAME_DURATION)

        ani.update(elapsed)

        buffer.fill('lightblue')
        x_offset = (0 if look_right else 1) * ANIMATION_NUM_FRAMES * SPRITE_SCALE
        rect = pygame.Rect(ani.frame_animations[0].frame_id * SPRITE_SCALE + x_offset,
                           ani.frame_animations[0].action_id * SPRITE_SCALE, SPRITE_SCALE, SPRITE_SCALE)
        buffer.blit(guy, (0, 0), rect)
        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
