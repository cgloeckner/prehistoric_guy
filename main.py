import pygame
import random

from platform import Platformer, Actor, Object, Platform
from tile import Tiling, RESOLUTION_X, RESOLUTION_Y, WORLD_SCALE


# objects row offsets
FOOD_OBJ: int = 0
DANGER_OBJ: int = 1
BONUS_OBJ: int = 2
WEAPON_OBJ: int = 3


def on_landed(actor: Actor, platform: Platform) -> None:
    # print(f'landing of\n\t{actor}\n\ton {platform}')
    pass


def on_collision(actor: Actor, platform: Platform) -> None:
    # print(f'collision between\n\t{actor}\n\tand {platform}')
    pass


def on_touch(actor: Actor, other: Actor) -> None:
    # print(f'touch between\n\t{actor}\n\tand {other}')
    pass


score = 0
plat = None


def create_food() -> None:
    global score

    # pick random position on random platform
    p = random.choice(plat.platforms)
    x = random.randrange(p.width)

    plat.objects.append(Object(p.x + x, p.y + 0.5, DANGER_OBJ))


def on_reach(actor: Actor, other: Object) -> None:
    global score
    global plat
    score += 1
    plat.objects.remove(other)

    create_food()



def populate_demo_scene(plat: Platformer) -> None:
    plat.actors.append(Actor(1.5, 3.5))
    plat.actors.append(Actor(7.5, 4.5))

    # horizontal platforms
    plat.platforms.append(Platform(0, 1.0, 3, 2))
    plat.platforms.append(Platform(3, 2.0, 1, 2))
    plat.platforms.append(Platform(3, 2.0, 1, 2))
    plat.platforms.append(Platform(4, 3.0, 1, 3))
    plat.platforms.append(Platform(6, 3.0, 4, 3))
    plat.platforms.append(Platform(7, 4.0, 1, 3))
    plat.platforms.append(Platform(7, 3.0, 2, 0))

    # NOTE: h=0 necessary to avoid collisions when jumping "into" the platform
    plat.platforms.append(Platform(1.0, 5.5, RESOLUTION_X // WORLD_SCALE - 2.0, 0.0))

    for i in range(10):
        create_food()


def main():
    global score
    global plat

    pygame.init()

    # get native resolution and factor for scaling
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= RESOLUTION_X
    native_height //= RESOLUTION_Y
    ui_scale_factor = max(1, min(native_width, native_height))
    # override it for debugging purpose
    #ui_scale_factor = 2

    # calculate window resolution and initialize screen
    window_width = RESOLUTION_X * ui_scale_factor
    window_height = RESOLUTION_Y * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height))
    buffer = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))
    clock = pygame.time.Clock()

    plat = Platformer(on_landed, on_collision, on_touch, on_reach)
    populate_demo_scene(plat)

    render = Tiling(buffer, clock, False)

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
