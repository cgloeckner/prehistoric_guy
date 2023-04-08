import pygame
import random
import math
import imgui
from typing import Optional

from imgui_wrapper import OpenGlWrapper

from constants import *
import platforms
import tiles
import animations
import factory
import editor
import controls


class Game(platforms.PhysicsListener, animations.AnimationListener):

    def __init__(self):
        self.score = 0
        self.obj_manager: Optional[factory.ObjectManager] = None

    def create_food(self) -> None:
        # pick random position on random platform
        p = random.choice(self.obj_manager.physics.platforms)
        x = random.randrange(p.width)

        self.obj_manager.create_object(x=p.x + x, y=p.y + 0.5, object_type=FOOD_OBJ)

    def populate_demo_scene(self, guy_sheet: pygame.Surface) -> None:
        self.obj_manager.create_actor_sprite(sprite_sheet=guy_sheet, x=2, y=5)
        self.obj_manager.create_actor_sprite(sprite_sheet=guy_sheet, x=6, y=5)

        # horizontal platforms
        self.obj_manager.create_platform(x=0, y=1, width=3, height=2)
        self.obj_manager.create_platform(x=2, y=2, width=2)
        self.obj_manager.create_platform(x=0, y=4, width=3)
        #self.obj_manager.create_platform(x=4, y=1, width=6,
        #                                 hover=platforms.Hovering(x=math.cos, y=math.sin, amplitude=1.5))
        self.obj_manager.create_platform(x=4, y=4, width=6, height=10)
        self.obj_manager.create_platform(x=5, y=6, width=4)

        # NOTE: h=0 necessary to avoid collisions when jumping "into" the platform
        self.obj_manager.create_platform(x=2.0, y=6, width=RESOLUTION_X // WORLD_SCALE - 2 - 3, height=0,
                                         hover=platforms.Hovering(y=math.cos, amplitude=-1))

        # ladders
        self.obj_manager.create_ladder(x=1, y=1, height=7)
        self.obj_manager.create_ladder(x=8, y=3, height=3)

        for i in range(10):
            self.create_food()

    # --- Physics Events ----------------------------------------------------------------------------------------------

    def on_land_on_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor landed on a platform.
        """
        # search corresponding animation
        for sprite in self.obj_manager.renderer.sprites:
            if sprite.actor == actor:
                action = animations.IDLE_ACTION
                delta_h = actor.fall_from_y - sprite.actor.y

                if delta_h > 2.5:
                    action = animations.LANDING_ACTION

                if delta_h > 4.0:
                    action = animations.DIE_ACTION

                animations.start(sprite.animation, action)
                return

    def on_falling(self, actor: platforms.Actor) -> None:
        """Triggered when the actor starts falling.
        """
        print('falling')

    def on_collide_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor runs into a platform.
        """
        print('colliding')

    def on_switch_platform(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        print('switching')

    def on_touch_actor(self, actor: platforms.Actor, other: platforms.Actor) -> None:
        """Triggered when the actor touches another actor.
        """
        print('touched actor')

    def on_reach_object(self, actor: platforms.Actor, obj: platforms.Object) -> None:
        """Triggered when the actor reaches an object.
        """
        self.score += 1
        self.obj_manager.destroy_object(obj)

        self.create_food()

    def on_reach_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor reaches a ladder.
        """
        print('reached ladder')

    def on_leave_ladder(self, actor: platforms.Actor, ladder: platforms.Ladder) -> None:
        """Triggered when the actor leaves a ladder.
        """
        print('left ladder')

    # --- Animation Events -

    def on_step(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a move animation finished.
        """
        print('step!')

    def on_climb(self, ani: animations.Animation) -> None:
        """Triggered when a cycle of a climbing animation finished.
        """
        print('climb!')

    def on_attack(self, ani: animations.Animation) -> None:
        """Triggered when an attack animation finished.
        """
        sprite = [sprite for sprite in self.obj_manager.renderer.sprites if sprite.animation == ani][0]
        self.obj_manager.create_projectile(x=sprite.actor.x + sprite.actor.face_x,
                                           y=sprite.actor.y + sprite.actor.radius, radius=platforms.OBJECT_RADIUS,
                                           speed=10.0, face_x=sprite.actor.face_x, object_type=WEAPON_OBJ)
        print('swing!')

    def on_impact_platform(self, proj: platforms.Projectile, platform: platforms.Platform) -> None:
        """Triggered when a projectile hits a platform.
        """
        self.obj_manager.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.obj_manager.destroy_projectile(proj)

    def on_impact_actor(self, proj: platforms.Projectile, actor: platforms.Actor) -> None:
        """Triggered when a projectile hits an actor.
        """
        sprite = [sprite for sprite in self.obj_manager.renderer.sprites if sprite.actor == actor][0]
        self.obj_manager.destroy_actor_sprite(sprite)
        self.obj_manager.create_object(x=proj.x, y=proj.y - platforms.OBJECT_RADIUS, object_type=proj.object_type)
        self.obj_manager.destroy_projectile(proj)



def main():
    pygame.init()

    # get native resolution and factor for scaling
    native_width, native_height = pygame.display.get_desktop_sizes()[0]
    native_width //= RESOLUTION_X
    native_height //= RESOLUTION_Y
    # ui_scale_factor = max(1, min(native_width, native_height))
    # override it for debugging purpose
    ui_scale_factor = 2

    # calculate window resolution and initialize screen
    window_width = RESOLUTION_X * ui_scale_factor
    window_height = RESOLUTION_Y * ui_scale_factor
    print(f'Resolution: {window_width}x{window_height}; Resize: {ui_scale_factor}')
    screen = pygame.display.set_mode((window_width, window_height), OpenGlWrapper.get_display_flags())
    buffer = pygame.Surface((RESOLUTION_X, RESOLUTION_Y))
    wrapper = OpenGlWrapper(screen)
    clock = pygame.time.Clock()

    guy = animations.flip_sprite_sheet(pygame.image.load('data/guy.png'), SPRITE_SCALE)

    game = Game()

    phys = platforms.Physics(game)
    anis = animations.Animating(game)
    render = tiles.Renderer(buffer, clock)

    game.obj_manager = factory.ObjectManager(phys, anis, render)
    game.populate_demo_scene(guy)

    editor_ui = editor.SceneEditor(screen, game.obj_manager)
    ctrl = controls.Player(render.sprites[0],
                           controls.Keybinding(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w, down=pygame.K_s,
                                               attack=pygame.K_SPACE, throw=pygame.K_RETURN))

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

            wrapper.process_event(event)

        editor_ui.update()
        ctrl.update()
        phys.update(elapsed)

        # limit pos to screen
        phys.actors[0].x = max(0, min(phys.actors[0].x, RESOLUTION_X // WORLD_SCALE))
        if phys.actors[0].y < 0:
            game.score -= 3
            if game.score < 0:
                game.score = 0
            phys.actors[0].y += RESOLUTION_Y // WORLD_SCALE

        anis.update(elapsed)

        # draw game
        buffer.fill('black')
        render.draw(phys, 0)
        phys.draw(buffer)

        score_surface = render.font.render(f'SCORE: {game.score}', False, 'black')
        wrapper.buffer.blit(score_surface, (0, 0))

        # draw imgui UI
        imgui.new_frame()
        editor_ui.draw()
        wrapper.buffer.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        wrapper.render()

        pygame.display.flip()

        pygame.display.set_caption('Prehistoric Guy')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
