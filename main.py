import pygame

from platform import Platformer, Actor, Platform

RESOLUTION_X: int = 320
RESOLUTION_Y: int = 240
WORLD_SCALE: int = RESOLUTION_X // 20


def draw_actor(ctx: pygame.Surface, actor: Actor) -> None:
    pos = (actor.pos_x * WORLD_SCALE, ctx.get_height() - actor.pos_y * WORLD_SCALE - actor.radius * WORLD_SCALE)
    pygame.draw.circle(ctx, 'blue', pos, actor.radius * WORLD_SCALE)


def draw_platform(ctx: pygame.Surface, platform: Platform, tiles: pygame.Surface) -> None:
    x1 = platform.x * WORLD_SCALE
    x2 = (platform.x + platform.width) * WORLD_SCALE
    y1 = ctx.get_height() - platform.y * WORLD_SCALE
    y2 = ctx.get_height() - (platform.y - platform.height) * WORLD_SCALE

    pygame.draw.line(ctx, 'red', (x1, y1), (x2, y1), 4)
    pygame.draw.line(ctx, 'red', (x1, y1), (x1, y2), 4)
    pygame.draw.line(ctx, 'red', (x2, y1), (x2, y2), 4)

    # ctx.blit(tiles, (x1, y), (256, 0, 256, 256))


def main():
    pygame.init()

    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= RESOLUTION_X
    native_height //= RESOLUTION_Y
    ui_scale_factor = max(1, min(native_width, native_height))

    # override it for debugging purpose
    ui_scale_factor = 2

    window_width = RESOLUTION_X * ui_scale_factor
    window_height = RESOLUTION_Y * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height))
    buffer = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))

    tiles = pygame.image.load('data/platforms.png')

    def on_landed(actor: Actor, platform: Platform) -> None:
        print(f'landed on {platform}')

    def on_collision(actor: Actor, platform: Platform) -> None:
        print(f'collided with {platform}')

    plat = Platformer(on_landed, on_collision)
    plat.actors.append(Actor(2.5, 5.5))

    # horizontal platforms
    plat.platforms.append(Platform(-4.0, 0.5, 4.0, 0.25))
    plat.platforms.append(Platform(0.0, 0.5, 4.0, 0.25))
    plat.platforms.append(Platform(4.0, 0.5, 4.0, 0.25))
    plat.platforms.append(Platform(8.0, 0.5, 4.0, 0.25))
    plat.platforms.append(Platform(16.0, 0.5, 4.0, 0.25))

    plat.platforms.append(Platform(6.0, 2.0, 4.0, 2.1))
    plat.platforms.append(Platform(7.0, 4.0, 2.0, 0.1))
    plat.platforms.append(Platform(14.0, 5.5, 4.0, 0.1))

    plat.platforms.append(Platform(11.0, 6.0, 2.0, 6.0))

    clock = pygame.time.Clock()
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
            for a in plat.actors:
                a.force_y = 1

        delta_x = 0.0
        if keys[pygame.K_a]:
            delta_x -= 1.0
        if keys[pygame.K_d]:
            delta_x += 1.0
        plat.actors[0].force_x = delta_x

        plat.update(elapsed)

        # limit pos to screen
        plat.actors[0].pos_x = max(0, min(plat.actors[0].pos_x, RESOLUTION_X // WORLD_SCALE))
        if plat.actors[0].pos_y < 0:
            plat.actors[0].pos_y += RESOLUTION_Y // WORLD_SCALE

        buffer.fill('black')

        # tiled background
        num_w = RESOLUTION_X // 256 + 1
        num_h = RESOLUTION_Y // 256 + 1
        for y in range(num_h):
            for x in range(num_w):
                buffer.blit(tiles, (x * 256, y * 256), (0, 0, 256, 256))

        # foreground
        for p in plat.platforms:
            draw_platform(buffer, p, tiles)
        for a in plat.actors:
            draw_actor(buffer, a)

        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        pygame.display.set_caption(f'Prehistoric Guy - FPS: {clock.get_fps():.1f}')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
