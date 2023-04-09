import pygame
import imgui

from constants import *
import platforms
import tiles
import animations
import factory
import editor
import controls
import widgets
import game
import state_machine


class DemoState(state_machine.State):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)

        self.guy = animations.flip_sprite_sheet(pygame.image.load('data/guy.png'), SPRITE_SCALE)

        self.manager = game.Manager()

        self.phys = platforms.Physics(self.manager)
        self.anis = animations.Animating(self.manager)
        self.render = tiles.Renderer(engine.buffer, engine.clock)

        self.manager.factory = factory.ObjectManager(self.phys, self.anis, self.render)
        self.manager.populate_demo_scene(self.guy)

        self.editor_ui = editor.SceneEditor(engine.screen, self.manager.factory)
        self.ctrl = controls.Player(self.render.sprites[0], controls.Keybinding(left=pygame.K_a, right=pygame.K_d,
                                                                                up=pygame.K_w, down=pygame.K_s,
                                                                                attack=pygame.K_SPACE))

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.ctrl.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        self.editor_ui.update()
        self.ctrl.update(elapsed_ms)
        self.phys.update(elapsed_ms)
        self.anis.update(elapsed_ms)

        # limit pos to screen
        self.ctrl.sprite.actor.x = max(0, min(self.ctrl.sprite.actor.x, RESOLUTION_X // WORLD_SCALE))
        if self.ctrl.sprite.actor.y < 0:
            self.manager.score -= 3
            if self.manager.score < 0:
                self.manager.score = 0
            self.ctrl.sprite.actor.y += RESOLUTION_Y // WORLD_SCALE

    def draw(self) -> None:
        self.render.draw(self.phys, 0)
        # phys.draw(buffer)

        score_surface = self.render.font.render(f'SCORE: {self.manager.score}', False, 'black')
        self.engine.buffer.blit(score_surface, (0, 0))

        throw_perc = self.ctrl.get_throwing_process()
        if throw_perc > 0.5:
            widgets.progress_bar(self.engine.buffer,
                                 int(self.ctrl.sprite.actor.x * WORLD_SCALE),
                                 RESOLUTION_Y - int(self.ctrl.sprite.actor.y * WORLD_SCALE + WORLD_SCALE),
                                 15, 3, throw_perc)

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(pygame.transform.scale_by(self.engine.buffer, self.engine.ui_scale_factor),
                                        (0, 0))
        self.engine.wrapper.render()


if __name__ == '__main__':
    game_engine = state_machine.Engine()
    pygame.display.set_caption('Prehistoric Guy')
    game_engine.push(DemoState(game_engine))
    game_engine.run()
