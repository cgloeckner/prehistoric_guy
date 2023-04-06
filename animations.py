import pygame
from dataclasses import dataclass

from constants import WORLD_SCALE


ANIMATION_FRAME_DURATION: int = 100
ANIMATION_NUM_FRAMES: int = 4

IDLE_ACTION: int = 0
MOVE_ACTION: int = 1
ATTACK_ACTION: int = 2
JUMP_ACTION: int = 3
LANDING_ACTION: int = 4
DIE_ACTION: int = 5


@dataclass
class Animation:
    # row and column index
    action_id: int = 0
    frame_id: int = 0
    # animation timing
    frame_time_ms: int = 0


def flip_sprite_sheet(src: pygame.Surface, tile_size: int) -> pygame.Surface:
    """Splits all sprite frames but keeps the logical order of the entire sprite sheet.
    """
    size = src.get_size()
    mirrored = pygame.transform.flip(src, flip_x=True, flip_y=False)
    dst = pygame.Surface(size, flags=pygame.SRCALPHA)

    for column in range(src.get_width() // tile_size):
        dst.blit(mirrored, (column * tile_size, 0), (size[0] - (column + 1) * tile_size, 0, tile_size, size[1]))

    return dst


def start(ani: Animation, action_id: int) -> None:
    """Resets the animation with the given action.
    """
    if ani.action_id == action_id:
        return

    ani.action_id = action_id
    ani.frame_id = 0
    ani.frame_time_ms = 0


class Animating(object):
    """Handles all frame set animations.
    """
    def __init__(self):
        self.animations = list()

    def update(self, elapsed_ms: int) -> None:
        """Updates all animations' frame durations. It automatically switches frames and loops/returns/freezes the
        animation once finished.
        """
        for ani in self.animations:
            # continue animation
            ani.frame_time_ms += elapsed_ms
            if ani.frame_time_ms >= ANIMATION_FRAME_DURATION:
                ani.frame_time_ms -= ANIMATION_FRAME_DURATION
                ani.frame_id += 1

                # handle animation type (loop, reset, freeze)
                if ani.frame_id == ANIMATION_NUM_FRAMES:
                    if ani.action_id in [IDLE_ACTION, MOVE_ACTION]:
                        # loop
                        ani.frame_id = 0
                    elif ani.action_id in [ATTACK_ACTION, LANDING_ACTION]:
                        # reset to idle
                        ani.frame_id = 0
                        ani.action_id = IDLE_ACTION
                    else:
                        # freeze at last frame
                        ani.frame_id -= 1


def main():
    pygame.init()

    # get native resolution and factor for scaling
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= WORLD_SCALE
    native_height //= WORLD_SCALE
    ui_scale_factor = max(1, min(native_width, native_height))
    ui_scale_factor //= 4

    # calculate window resolution and initialize screen
    window_width = WORLD_SCALE * ui_scale_factor
    window_height = WORLD_SCALE * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height))
    buffer = pygame.Surface((WORLD_SCALE, WORLD_SCALE))
    clock = pygame.time.Clock()

    guy = pygame.image.load('data/guy.png')
    guy2 = flip_sprite_sheet(guy, WORLD_SCALE)
    sprite_sheet = guy

    ani = Animating()
    ani.animations.append(Animation())

    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            sprite_sheet = guy2
        if keys[pygame.K_d]:
            sprite_sheet = guy
        if keys[pygame.K_1]:
            start(ani.animations[0], IDLE_ACTION)
        if keys[pygame.K_2]:
            start(ani.animations[0], MOVE_ACTION)
        if keys[pygame.K_3]:
            start(ani.animations[0], ATTACK_ACTION)
        if keys[pygame.K_4]:
            start(ani.animations[0], JUMP_ACTION)
        if keys[pygame.K_5]:
            start(ani.animations[0], DIE_ACTION)

        ani.update(elapsed)

        buffer.fill('lightblue')
        rect = pygame.Rect(ani.animations[0].frame_id * WORLD_SCALE, ani.animations[0].action_id * WORLD_SCALE,
                           WORLD_SCALE, WORLD_SCALE)
        buffer.blit(sprite_sheet, (0, 0), rect)

        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
