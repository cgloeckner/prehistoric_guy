import pygame

from platform import Platformer, Actor, Platform

RESOLUTION_X: int = 320
RESOLUTION_Y: int = 240
WORLD_SCALE: int = RESOLUTION_X // 10


def draw_actor(ctx: pygame.Surface, actor: Actor) -> None:
    pos = (actor.pos_x * WORLD_SCALE, ctx.get_height() - actor.pos_y * WORLD_SCALE - actor.radius * WORLD_SCALE)
    pygame.draw.circle(ctx, 'blue', pos, actor.radius * WORLD_SCALE)


def draw_platform(ctx: pygame.Surface, platform: Platform, tile: pygame.Surface) -> None:
    x = platform.x * WORLD_SCALE
    y = ctx.get_height() - platform.y * WORLD_SCALE

    for i in range(int(platform.width)):
        ctx.blit(tile, (x + i * WORLD_SCALE, y), (0, 0, WORLD_SCALE, WORLD_SCALE))
        for j in range(int(platform.height)):
            ctx.blit(tile, (x + i * WORLD_SCALE, y + (j+1) * WORLD_SCALE), (0, WORLD_SCALE, WORLD_SCALE, WORLD_SCALE))

    # FIXME: remove debug drawing
    # x2 = (platform.x + platform.width) * WORLD_SCALE
    # y2 = ctx.get_height() - (platform.y - platform.height) * WORLD_SCALE
    # pygame.draw.line(ctx, 'red', (x, y), (x2, y), 4)
    # pygame.draw.line(ctx, 'red', (x, y), (x, y2), 4)
    # pygame.draw.line(ctx, 'red', (x2, y), (x2, y2), 4)


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

    background = pygame.image.load('data/background.png')
    tile = pygame.image.load('data/tile.png')

    def on_landed(actor: Actor, platform: Platform) -> None:
        # print(f'landing of\n\t{actor}\n\ton {platform}')
        pass

    def on_collision(actor: Actor, platform: Platform) -> None:
        # print(f'collision between\n\t{actor}\n\tand {platform}')
        pass

    def on_touch(actor: Actor, other: Actor) -> None:
        # print(f'touch between\n\t{actor}\n\tand {other}')
        pass

    plat = Platformer(on_landed, on_collision, on_touch)
    plat.actors.append(Actor(1.5, 3.5))
    plat.actors.append(Actor(7.5, 4.5))

    # horizontal platforms
    plat.platforms.append(Platform(0.0, 1.0, 4.0, 0.5))
    plat.platforms.append(Platform(3.0, 1.5, 2.0, 1.5))
    plat.platforms.append(Platform(3.5, 2.0, 1.0, 2.0))
    plat.platforms.append(Platform(4.0, 3.0, 1.0, 3.0))
    plat.platforms.append(Platform(6.0, 2.5, 4.0, 2.5))
    plat.platforms.append(Platform(7.0, 3.5, 2.0, 0.25))
    plat.platforms.append(Platform(1.0, 5.5, RESOLUTION_X // WORLD_SCALE - 2.0, 0.5))

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
            plat.actors[0].force_y = 1

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
        bg_size = background.get_size()
        num_w = RESOLUTION_X // bg_size[0] + 1
        num_h = RESOLUTION_Y // bg_size[1] + 1
        for y in range(num_h):
            for x in range(num_w):
                buffer.blit(background, (x * bg_size[0], y * bg_size[1]), (0, 0, bg_size[0], bg_size[1]))

        # foreground
        plat.platforms.sort(key=lambda plat: plat.y)
        for p in plat.platforms:
            draw_platform(buffer, p, tile)
        for a in plat.actors:
            draw_actor(buffer, a)

        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        pygame.display.set_caption(f'Prehistoric Guy - FPS: {clock.get_fps():.1f}')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
