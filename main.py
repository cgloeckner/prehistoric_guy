import pygame
import imgui

import platformer
import editor
import state_machine


class DemoState(state_machine.State):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = platformer.Cache()
        self.font = self.cache.get_font()

        self.manager = platformer.ObjectManager(self.cache, engine.buffer)
        self.manager.populate_demo_scene(self.cache)

        self.editor_ui = editor.SceneEditor(engine.screen, self.manager)

        phys_actor = self.manager.physics.get_by_id(self.manager.player_character.object_id)
        ani_actor = self.manager.animation.get_by_id(self.manager.player_character.object_id)
        keys = platformer.Keybinding(left=pygame.K_a, right=pygame.K_d, up=pygame.K_w, down=pygame.K_s,
                                     attack=pygame.K_SPACE)
        self.ctrl = platformer.Player(phys_actor, ani_actor, keys)

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
            self.manager.renderer.move_camera(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.manager.renderer.move_camera(1, 0)
        if keys[pygame.K_UP]:
            self.manager.renderer.move_camera(0, 1)
        if keys[pygame.K_DOWN]:
            self.manager.renderer.move_camera(0, -1)

        self.editor_ui.update()
        self.ctrl.update(elapsed_ms)
        self.manager.update(elapsed_ms)

        for enemy in self.manager.chars.characters:
            if enemy == self.manager.player_character:
                continue
            ani_enemy = self.manager.animation.get_by_id(enemy.object_id)
            if ani_enemy.action_id in [platformer.DIE_ACTION, platformer.ATTACK_ACTION,
                                       platformer.THROW_ACTION, platformer.LANDING_ACTION]:
                continue
            phys_enemy = self.manager.physics.get_by_id(enemy.object_id)
            if phys_enemy.anchor is None:
                continue
            left_bound = phys_enemy.anchor.x + phys_enemy.anchor.width * 0.05
            right_bound = phys_enemy.anchor.x + phys_enemy.anchor.width * 0.95
            if phys_enemy.x < left_bound:
                phys_enemy.face_x = 1.0
            elif phys_enemy.x > right_bound:
                phys_enemy.face_x = -1.0
            phys_enemy.force_x = phys_enemy.face_x
            platformer.start(ani_enemy, platformer.MOVE_ACTION)

        # limit pos to screen
        self.ctrl.phys_actor.x = max(0.0, min(self.ctrl.phys_actor.x, platformer.RESOLUTION_X / platformer.WORLD_SCALE))
        if self.ctrl.phys_actor.y < 0:
            self.ctrl.phys_actor.y += platformer.RESOLUTION_Y // platformer.WORLD_SCALE

    def draw(self) -> None:
        self.manager.renderer.draw(0)
        # phys.draw(buffer)

        char_pc = self.manager.player_character
        platformer.hud.hud_icons(self.engine.buffer, self.hud, char_pc)

        """
        hud_str = f'{c.hit_points}/{c.max_hit_points} HP, {c.num_axes}/{c.max_num_axes} Axes'
        hud_surface = self.render.font.render(hud_str, False, 'white')
        self.engine.buffer.blit(hud_surface, (0, 0))
        """

        throw_perc = self.ctrl.get_throwing_process()
        phys_pc = self.manager.physics.get_by_id(char_pc.object_id)
        if throw_perc > 0.5:
            platformer.hud.throw_progress(self.engine.buffer, self.manager.renderer.camera, phys_pc, throw_perc)

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, platformer.RESOLUTION_Y - fps_surface.get_height()))

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()


if __name__ == '__main__':
    game_engine = state_machine.Engine(platformer.RESOLUTION_X, platformer.RESOLUTION_Y)
    pygame.display.set_caption('Prehistoric Guy')
    game_engine.push(DemoState(game_engine))
    game_engine.run()
