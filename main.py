import pygame
import random
import math
import imgui
from typing import Optional, List

from constants import *
import platforms
import tiles
import animations
import factory
from imgui_wrapper import OpenGlWrapper


# objects row offsets
FOOD_OBJ: int = 0
DANGER_OBJ: int = 1
BONUS_OBJ: int = 2
WEAPON_OBJ: int = 3


class Game(platforms.PhysicsListener, animations.AnimationListener):

    def __init__(self):
        self.score = 0
        self.obj_manager: Optional[factory.ObjectManager] = None

    def get_hovered(self, screen: pygame.Surface) -> List:
        # transform screen coordinates to game coordinates (keep in mind that the screen was upscaled by x2)
        x, y = pygame.mouse.get_pos()
        y = screen.get_height() - y
        x //= 2
        y //= 2
        x /= WORLD_SCALE
        y /= WORLD_SCALE
        pos = pygame.math.Vector2(x, y)

        # collect all hoverable objects
        hovered = list()
        for platform in self.obj_manager.physics.platforms:
            h = platform.height if platform.height > 0.0 else platforms.OBJECT_RADIUS
            if platform.x <= x <= platform.x + platform.width and platform.y - h <= y <= platform.y:
                hovered.append(platform)

        for actor in self.obj_manager.physics.actors:
            actor_pos = pygame.math.Vector2(actor.pos_x, actor.pos_y + actor.radius)
            distance = pos.distance_squared_to(actor_pos)
            if distance <= actor.radius ** 2:
                hovered.append(actor)

        for obj in self.obj_manager.physics.objects:
            obj_pos = pygame.math.Vector2(obj.pos_x, obj.pos_y + platforms.OBJECT_RADIUS)
            distance = pos.distance_squared_to(obj_pos)
            if distance <= platforms.OBJECT_RADIUS ** 2:
                hovered.append(obj)

        return hovered

    def create_food(self) -> None:
        # pick random position on random platform
        p = random.choice(self.obj_manager.physics.platforms)
        x = random.randrange(p.width)

        self.obj_manager.create_object(pos_x=p.x + x, pos_y=p.y + 0.5, object_type=FOOD_OBJ)

    def populate_demo_scene(self, guy_sheet: pygame.Surface) -> None:
        self.obj_manager.create_actor(sprite_sheet=guy_sheet, pos_x=1.5, pos_y=3.5)
        self.obj_manager.create_actor(sprite_sheet=guy_sheet, pos_x=7.5, pos_y=4.5)

        # horizontal platforms
        self.obj_manager.create_platform(x=0, y=1, width=3, height=2)
        self.obj_manager.create_platform(x=-0.5, y=3.5, width=1, height=4)
        self.obj_manager.create_platform(x=0, y=3, width=1, height=4)
        self.obj_manager.create_platform(x=0.5, y=2, width=1, height=4)
        self.obj_manager.create_platform(x=3, y=2, width=1, height=0,
                                         float_x=lambda x: -math.cos(x/2),
                                         float_y=lambda y: 2*math.sin(y))
        self.obj_manager.create_platform(x=4, y=3, width=1, height=3)
        self.obj_manager.create_platform(x=6, y=3, width=4, height=3)
        self.obj_manager.create_platform(x=7, y=4, width=1, height=3)
        self.obj_manager.create_platform(x=3, y=5, width=2, height=0, float_y=math.cos)
        self.obj_manager.create_platform(x=7, y=5, width=2, height=0, float_x=math.cos)

        # NOTE: h=0 necessary to avoid collisions when jumping "into" the platform
        self.obj_manager.create_platform(x=1.0, y=6, width=RESOLUTION_X // WORLD_SCALE - 2 - 3, height=0,
                                         float_y=lambda y: -math.sin(y))

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

    def on_switching(self, actor: platforms.Actor, platform: platforms.Platform) -> None:
        """Triggered when the actor switches to the given platform as an anchor.
        """
        print('wuuuhuu')

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


selected = None


def main():
    global selected

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

    def demo_ui():
        global selected

        imgui.new_frame()

        if selected is None:
            return

        imgui.begin(type(selected).__name__, False)

        if isinstance(selected, platforms.Platform):
            _, selected.x = imgui.input_float('x', selected.x, step=0.1)
            _, selected.y = imgui.input_float('y', selected.y, step=0.1)
            _, selected.width = imgui.input_float('width', selected.width, step=0.1)
            _, selected.height = imgui.input_float('height', selected.height, step=0.1)
            clicked, current = imgui.combo('float_x', 0, ['None', 'sin', '-sin', 'cos', '-cos'])
            if clicked:
                if current == 'None': selected.float_x = None
                if current == 'sin': selected.float_x = math.sin
                if current == '-sin': selected.float_x = lambda v: -math.sin(v)
                if current == 'cos': selected.float_x = math.cos
                if current == '-cos': selected.float_x = lambda v: -math.cos(v)
            clicked, current = imgui.combo('float_y', 0, ['None', 'sin', '-sin', 'cos', '-cos'])
            if clicked:
                if current == 'None': selected.float_y = None
                if current == 'sin': selected.float_y = math.sin
                if current == '-sin': selected.float_y = lambda v: -math.sin(v)
                if current == 'cos': selected.float_y = math.cos
                if current == '-cos': selected.float_y = lambda v: -math.cos(v)
            if imgui.button("Close"):
                selected = None
        else:
            imgui.text('Not Implemented Yet')

        imgui.end()

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

        if pygame.mouse.get_pressed()[0]:
            if len(render.hover) > 0 and selected is None:
                selected = render.hover[0]

        render.hover = game.get_hovered(screen)

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
        # phys.draw(buffer)

        score_surface = render.font.render(f'SCORE: {game.score}', False, 'black')
        wrapper.buffer.blit(score_surface, (0, 0))

        demo_ui()

        wrapper.buffer.blit(pygame.transform.scale_by(buffer, ui_scale_factor), (0, 0))
        wrapper.render()

        pygame.display.flip()

        pygame.display.set_caption('Prehistoric Guy')
        elapsed = clock.tick(60)

    pygame.quit()


if __name__ == '__main__':
    main()
