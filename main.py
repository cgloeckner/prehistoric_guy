import pygame
import imgui

from constants import *
import resources
import platforms
import tiles
import animations
import factory
import editor
import controls
import widgets
import game
import state_machine


HEART_HUD: int = 0
WEAPON_HUD: int = 1


class DemoState(state_machine.State):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = resources.Cache()

        self.manager = game.Manager()
        self.phys = platforms.Physics(self.manager)
        self.anis = animations.Animating(self.manager)
        self.render = tiles.Renderer(self.cache, engine.buffer, engine.clock)

        self.manager.factory = factory.ObjectManager(self.phys, self.anis, self.render)
        self.manager.populate_demo_scene(self.cache)

        self.editor_ui = editor.SceneEditor(engine.screen, self.manager.factory)
        self.ctrl = controls.Player(self.manager.player_character,
                                    controls.Keybinding(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w,
                                                        down=pygame.K_s, attack=pygame.K_SPACE))

        self.hud = pygame.image.load('data/hud.png')

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.ctrl.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.render.move_camera(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.render.move_camera(1, 0)
        if keys[pygame.K_UP]:
            self.render.move_camera(0, 1)
        if keys[pygame.K_DOWN]:
            self.render.move_camera(0, -1)

        self.editor_ui.update()
        self.ctrl.update(elapsed_ms)
        self.phys.update(elapsed_ms)
        self.anis.update(elapsed_ms)

        for enemy in self.manager.enemies:
            if enemy.sprite.actor.anchor is None:
                continue
            left_bound = enemy.sprite.actor.anchor.x + enemy.sprite.actor.anchor.width * 0.05
            right_bound = enemy.sprite.actor.anchor.x + enemy.sprite.actor.anchor.width * 0.95
            if enemy.sprite.actor.x < left_bound:
                enemy.sprite.actor.face_x = 1.0
            elif enemy.sprite.actor.x > right_bound:
                enemy.sprite.actor.face_x = -1.0
            enemy.sprite.actor.force_x = enemy.sprite.actor.face_x
            animations.start(enemy.sprite.animation, animations.MOVE_ACTION)

        # limit pos to screen
        self.ctrl.character.sprite.actor.x = max(0.0,
                                                 min(self.ctrl.character.sprite.actor.x, RESOLUTION_X / WORLD_SCALE))
        if self.ctrl.character.sprite.actor.y < 0:
            self.ctrl.character.sprite.actor.y += RESOLUTION_Y // WORLD_SCALE

    def draw(self) -> None:
        self.render.draw(self.phys, 0)
        # phys.draw(buffer)

        c = self.ctrl.character
        for i in range(c.hit_points):
            self.engine.buffer.blit(self.hud, (i * OBJECT_SCALE, 0),
                                    (0 * OBJECT_SCALE, HEART_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))
        for i in range(c.num_axes):
            self.engine.buffer.blit(self.hud, (i * OBJECT_SCALE, OBJECT_SCALE),
                                    (0 * OBJECT_SCALE, WEAPON_HUD * OBJECT_SCALE, OBJECT_SCALE, OBJECT_SCALE))
        """
        hud_str = f'{c.hit_points}/{c.max_hit_points} HP, {c.num_axes}/{c.max_num_axes} Axes'
        hud_surface = self.render.font.render(hud_str, False, 'white')
        self.engine.buffer.blit(hud_surface, (0, 0))
        """

        throw_perc = self.ctrl.get_throwing_process()
        if throw_perc > 0.5:
            widgets.progress_bar(self.engine.buffer,
                                 int(self.ctrl.character.sprite.actor.x * WORLD_SCALE) - self.render.camera.x,
                                 RESOLUTION_Y - (-self.render.camera.y + int(self.ctrl.character.sprite.actor.y * WORLD_SCALE + WORLD_SCALE)),
                                 15, 3, throw_perc)

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()


if __name__ == '__main__':
    game_engine = state_machine.Engine()
    pygame.display.set_caption('Prehistoric Guy')
    game_engine.push(DemoState(game_engine))
    game_engine.run()
