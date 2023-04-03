import pygame

from platform import Platformer, Actor, Platform


def draw_actor(ctx: pygame.Surface, actor: Actor) -> None:
    pygame.draw.circle(ctx, 'yellow', (actor.pos_x * 64, ctx.get_height() - actor.pos_y * 64 - 16), 16)


def draw_platform(ctx: pygame.Surface, platform: Platform, tiles: pygame.Surface) -> None:
    x1 = platform.left * 64
    y = ctx.get_height() - platform.bottom * 64
    x2 = (platform.left + platform.width) * 64
    #pygame.draw.line(ctx, 'red', (x1, y), (x2, y), 2)
    ctx.blit(tiles, (x1, y), (256, 0, 256, 256))


def main():
    pygame.init()

    # pick half of desktop resolution
    # NOTE: later pixel doubling for full screen
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    window_width = native_width // 2
    window_height = native_height // 2
    print(f'Resolution: {window_width}x{window_height}')
    screen = pygame.display.set_mode((window_width, window_height))

    tiles = pygame.image.load('data/platforms.png')

    plat = Platformer()
    plat.actors.append(Actor(2.5, 1.0))
    plat.actors.append(Actor(3.0, 8.0))
    plat.platforms.append(Platform(-4.0, 0.5, 4.0))
    plat.platforms.append(Platform(0.0, 0.5, 4.0))
    plat.platforms.append(Platform(4.0, 0.5, 4.0))
    plat.platforms.append(Platform(8.0, 0.5, 4.0))
    plat.platforms.append(Platform(12.0, 0.5, 4.0))
    plat.platforms.append(Platform(2.0, 2.0, 4.0))
    plat.platforms.append(Platform(1.5, 4.0, 4.0))
    plat.platforms.append(Platform(7.0, 4.0, 4.0))
    plat.platforms.append(Platform(1.0, 5.5, 4.0))
    plat.platforms.append(Platform(8.0, 7.0, 4.0))

    plat.platforms.sort(key=lambda p: -p.bottom)

    clock = pygame.time.Clock()
    running = True
    elapsed = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            plat.actors[0].force_y = 1

        delta_x = 0.0
        if keys[pygame.K_a]:
            delta_x -= 1.0
        if keys[pygame.K_d]:
            delta_x += 1.0
        plat.actors[0].force_x = delta_x

        plat.update(elapsed)

        # limit x-pos to screen
        plat.actors[0].pos_x = max(0, min(plat.actors[0].pos_x, window_width // 64))

        screen.fill('black')

        # tiled background
        num_w = window_width // 256 + 1
        num_h = window_height // 256 + 1
        for y in range(num_h):
            for x in range(num_w):
                screen.blit(tiles, (x * 256, y * 256), (0, 0, 256, 256))

        # foreground
        for p in plat.platforms:
            draw_platform(screen, p, tiles)
        for a in plat.actors:
            draw_actor(screen, a)
        pygame.display.flip()

        pygame.display.set_caption(f'Prehistoric Guy - FPS: {clock.get_fps():.1f}')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
