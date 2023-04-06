import pygame
import random
from typing import Optional

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


class Game(platforms.PhysicsListener, animations.AnimationListener):

    def __init__(self):
        self.score = 0
        self.obj_manager: Optional[factory.ObjectManager] = None

    def create_food(self) -> None:
        # pick random position on random platform
        p = random.choice(self.obj_manager.physics.platforms)
        x = random.randrange(p.width)

        self.obj_manager.create_object(pos_x=p.x + x, pos_y=p.y + 0.5, object_type=DANGER_OBJ)

    def populate_demo_scene(self, guy_sheet: pygame.Surface) -> None:
        self.obj_manager.create_actor(sprite_sheet=guy_sheet, pos_x=1.5, pos_y=3.5)
        self.obj_manager.create_actor(sprite_sheet=guy_sheet, pos_x=7.5, pos_y=4.5)

        # horizontal platforms
        self.obj_manager.create_platform(x=0, y=1.0, width=3, height=2)
        self.obj_manager.create_platform(x=3, y=2.0, width=1, height=2)
        self.obj_manager.create_platform(x=3, y=2.0, width=1, height=2)
        self.obj_manager.create_platform(x=4, y=3.0, width=1, height=3)
        self.obj_manager.create_platform(x=6, y=3.0, width=4, height=3)
        self.obj_manager.create_platform(x=7, y=4.0, width=1, height=3)
        self.obj_manager.create_platform(x=7, y=3.0, width=2, height=0)

        # NOTE: h=0 necessary to avoid collisions when jumping "into" the platform
        self.obj_manager.create_platform(x=1.0, y=5, width=RESOLUTION_X // WORLD_SCALE - 2, height=0)

        for i in range(10):
            self.create_food()

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_landing(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor landed on a platform.
        """
        # search corresponding animation
        for sprite in self.obj_manager.renderer.sprites:
            if sprite.actor == actor:
                action = animations.IDLE_ACTION
                delta_h = actor.fall_from_y - sprite.actor.pos_y
                print(delta_h)

                if delta_h > 2.5:
                    action = animations.LANDING_ACTION

                if delta_h > 4.0:
                    action = animations.DIE_ACTION

                animations.start(sprite.animation, action)
                return

    def on_falling(self, actor: platforms.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        print('oooh!')

    def on_colliding(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        print('buff!')

    def on_touching(self, actor: platforms.Actor, other: platforms.Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        print('bing!')

    def on_reaching(self, actor: platforms.Actor, obj: platforms.Object) -> None:
        """Triggered when the actor reaches an object.
        """
        self.score += 1
        self.obj_manager.destroy_object(obj)

        self.create_food()

    # --- Animation Events -

    def on_step(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        print('step!')

    def on_attack(self, ani: animations.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        print('swing!')


def main():
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

    guy = animations.flip_sprite_sheet(pygame.image.load('data/guy.png'), SPRITE_SCALE)

    game = Game()

    phys = platforms.Physics(game)
    anis = animations.Animating(game)
    render = tiles.Renderer(buffer, clock, True)

    game.obj_manager = factory.ObjectManager(phys, anis, render)
    game.populate_demo_scene(guy)

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

        if render.sprites[0].animation.action_id != animations.DIE_ACTION:
            if keys[pygame.K_SPACE]:
                animations.start(render.sprites[0].animation, animations.ATTACK_ACTION)
                render.sprites[0].actor.force_x = 0

            else:
                if keys[pygame.K_w]:
                    render.sprites[0].actor.force_y = 1
                    animations.start(render.sprites[0].animation, animations.JUMP_ACTION)

                delta_x = 0.0
                if keys[pygame.K_a]:
                    delta_x -= 1.0
                if keys[pygame.K_d]:
                    delta_x += 1.0
                if render.sprites[0].animation.action_id in [animations.IDLE_ACTION, animations.MOVE_ACTION]:
                    if delta_x != 0.0:
                        animations.start(render.sprites[0].animation, animations.MOVE_ACTION)
                    else:
                        animations.start(render.sprites[0].animation, animations.IDLE_ACTION)
                render.sprites[0].actor.force_x = delta_x

        if render.sprites[1].animation.action_id != animations.DIE_ACTION:
            if keys[pygame.K_RETURN]:
                animations.start(render.sprites[1].animation, animations.ATTACK_ACTION)
                render.sprites[1].actor.force_x = 0

            else:
                if keys[pygame.K_UP]:
                    render.sprites[1].actor.force_y = 1
                    animations.start(render.sprites[1].animation, animations.JUMP_ACTION)

                delta_x = 0.0
                if keys[pygame.K_LEFT]:
                    delta_x -= 1.0
                if keys[pygame.K_RIGHT]:
                    delta_x += 1.0

                if render.sprites[1].animation.action_id in [animations.IDLE_ACTION, animations.MOVE_ACTION]:
                    if delta_x != 0.0:
                        animations.start(render.sprites[1].animation, animations.MOVE_ACTION)
                    else:
                        animations.start(render.sprites[1].animation, animations.IDLE_ACTION)
                render.sprites[1].actor.force_x = delta_x

        phys.update(elapsed)

        # limit pos to screen
        phys.actors[0].pos_x = max(0, min(phys.actors[0].pos_x, RESOLUTION_X // WORLD_SCALE))
        if phys.actors[0].pos_y < 0:
            game.score -= 3
            if game.score < 0:
                game.score = 0
            phys.actors[0].pos_y += RESOLUTION_Y // WORLD_SCALE

        phys.actors[1].pos_x = max(0, min(phys.actors[1].pos_x, RESOLUTION_X // WORLD_SCALE))
        if phys.actors[1].pos_y < 0:
            phys.actors[1].pos_y += RESOLUTION_Y // WORLD_SCALE

        anis.update(elapsed)

        buffer.fill('black')
        render.draw(phys, 0)

        score_surface = render.font.render(f'SCORE: {game.score}', False, 'black')
        buffer.blit(score_surface, (0, 0))

        screen.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        pygame.display.flip()

        pygame.display.set_caption('Prehistoric Guy')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
