import pygame
import random

import platforms
import tiles
import animations
import factory
from constants import *


# objects row offsets
FOOD_OBJ: int = 0
DANGER_OBJ: int = 1
BONUS_OBJ: int = 2
WEAPON_OBJ: int = 3



def on_landed(actor: platforms.Actor, platform: platforms.Platform) -> None:
    # print(f'landing of\n\t{actor}\n\ton {platform}')
    pass


def on_collision(actor: platforms.Actor, platform: platforms.Platform) -> None:
    # print(f'collision between\n\t{actor}\n\tand {platform}')
    pass


def on_touch(actor: platforms.Actor, other: platforms.Actor) -> None:
    # print(f'touch between\n\t{actor}\n\tand {other}')
    pass


score: int = 0
obj_man: factory.ObjectManager = None


def create_food() -> None:
    global score
    global obj_man

    # pick random position on random platform
    p = random.choice(obj_man.physics.platforms)
    x = random.randrange(p.width)

    obj_man.create_object(pos_x=p.x + x, pos_y=p.y + 0.5, object_type=DANGER_OBJ)


def on_reach(actor: platforms.Actor, other: platforms.Object) -> None:
    global score
    global obj_man
    score += 1
    obj_man.destroy_object(other)

    create_food()


def populate_demo_scene(obj_manager: factory.ObjectManager) -> None:
    obj_manager.create_actor(pos_x=1.5, pos_y=3.5)
    obj_manager.create_actor(pos_x=7.5, pos_y=4.5)

    # horizontal platforms
    obj_manager.create_platform(x=0, y=1.0, width=3, height=2)
    obj_manager.create_platform(x=3, y=2.0, width=1, height=2)
    obj_manager.create_platform(x=3, y=2.0, width=1, height=2)
    obj_manager.create_platform(x=4, y=3.0, width=1, height=3)
    obj_manager.create_platform(x=6, y=3.0, width=4, height=3)
    obj_manager.create_platform(x=7, y=4.0, width=1, height=3)
    obj_manager.create_platform(x=7, y=3.0, width=2, height=0)

    # NOTE: h=0 necessary to avoid collisions when jumping "into" the platform
    obj_manager.create_platform(x=1.0, y=5.5, width=RESOLUTION_X // WORLD_SCALE - 2, height=0)

    for i in range(10):
        create_food()


def main():
    global score
    global obj_man

    pygame.init()

    # get native resolution and factor for scaling
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= RESOLUTION_X
    native_height //= RESOLUTION_Y
    ui_scale_factor = max(1, min(native_width, native_height))
    # override it for debugging purpose
    ui_scale_factor //= 2

    # calculate window resolution and initialize screen
    window_width = RESOLUTION_X * ui_scale_factor
    window_height = RESOLUTION_Y * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height))
    buffer = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))
    clock = pygame.time.Clock()

    plat = platforms.Physics(on_landed, on_collision, on_touch, on_reach)
    anis = animations.Animation()
    render = tiles.Renderer(buffer, clock, False)

    obj_man = factory.ObjectManager(plat, anis, render)
    populate_demo_scene(obj_man)

    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                    pygame.key.get_mods() & pygame.KMOD_ALT:
                # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
                pass

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            plat.actors[0].force_y = 1

        delta_x = 0.0
        if keys[pygame.K_a]:
            delta_x -= 1.0
        if keys[pygame.K_d]:
            delta_x += 1.0
        plat.actors[0].force_x = delta_x

        if keys[pygame.K_UP]:
            plat.actors[1].force_y = 1

        delta_x = 0.0
        if keys[pygame.K_LEFT]:
            delta_x -= 1.0
        if keys[pygame.K_RIGHT]:
            delta_x += 1.0
        plat.actors[1].force_x = delta_x

        plat.update(elapsed)

        # limit pos to screen
        plat.actors[0].pos_x = max(0, min(plat.actors[0].pos_x, RESOLUTION_X // WORLD_SCALE))
        if plat.actors[0].pos_y < 0:
            score -= 3
            if score < 0:
                score = 0
            plat.actors[0].pos_y += RESOLUTION_Y // WORLD_SCALE
        plat.actors[1].pos_x = max(0, min(plat.actors[1].pos_x, RESOLUTION_X // WORLD_SCALE))
        if plat.actors[1].pos_y < 0:
            plat.actors[1].pos_y += RESOLUTION_Y // WORLD_SCALE

        buffer.fill('black')
        render.draw(plat, 0)

        score_surface = render.font.render(f'SCORE: {score}', False, 'black')
        buffer.blit(score_surface, (0, 0))

        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        pygame.display.set_caption('Prehistoric Guy')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
