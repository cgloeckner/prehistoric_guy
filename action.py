import pygame
import math
import imgui

from core import constants, resources

from platformer import editor, scene
from platformer import controls, physics

import state_machine


class GameState(state_machine.State):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = resources.Cache()

        # --- loading some resources ----------------------------------------------------------------------------------
        self.font = self.cache.get_font()
        generic_guy = self.cache.get_sprite_sheet('guy')
        blue_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(hue=216),
                                                  constants.SPRITE_CLOTHES_COLORS)
        grey_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(saturation=0),
                                                  constants.SPRITE_CLOTHES_COLORS)

        # --- setup object manager with player character ---------------------------------------------------------------
        self.scene = scene.Scene(self.cache, engine.buffer)
        player_char_actor = self.scene.factory.create_character(sprite_sheet=blue_guy, x=2, y=5, max_hit_points=5,
                                                                num_axes=10)
        self.scene.factory.create_player(player_char_actor,
                                         keys=controls.Keybinding(left_key=pygame.K_a, right_key=pygame.K_d,
                                                                  up_key=pygame.K_w, down_key=pygame.K_s,
                                                                  attack_key=pygame.K_SPACE))

        phys_actor = self.scene.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)
        #self.manager.camera.follow.append(phys_actor)

        # --- create demo scene ---------------------------------------------------------------------------------------
        self.scene.factory.create_enemy(sprite_sheet=grey_guy, x=6.5, y=6.5, max_hit_points=2, num_axes=0)
        self.scene.factory.create_enemy(sprite_sheet=grey_guy, x=6.5, y=4.5, max_hit_points=2, num_axes=0)

        # horizontal platforms
        self.scene.factory.ctx.physics.create_platform(x=1, y=1, width=3, height=1)
        self.scene.factory.ctx.physics.create_platform(x=1, y=6, width=3)
        self.scene.factory.ctx.physics.create_platform(x=7, y=2, width=3, height=2)
        self.scene.factory.ctx.physics.create_platform(x=2, y=2, width=2)
        self.scene.factory.ctx.physics.create_platform(x=0, y=4, width=3)
        self.scene.factory.ctx.physics.create_platform(x=6, y=1, width=3)
        for i in range(100):
            self.scene.factory.ctx.physics.create_platform(x=10 + i, y=0, width=1, height=1 + i)
        self.scene.factory.ctx.physics.create_platform(x=5, y=6, width=4)

        self.scene.factory.ctx.physics.create_platform(x=3, y=7, width=1,
                                                       hover=physics.Hovering(x=math.cos, amplitude=-2))

        self.scene.factory.ctx.physics.create_platform(x=1, y=11, width=12)

        self.scene.factory.create_random_object()
        self.scene.factory.ctx.physics.create_object(x=1, y=1, object_type=constants.ObjectType.FOOD)

        self.scene.factory.ctx.physics.create_platform(x=-12, y=0, width=15)
        self.scene.factory.ctx.physics.create_platform(x=-8, y=1, width=5, height=5)
        self.scene.factory.ctx.physics.create_platform(x=-12, y=0, width=3, height=10)

        # ladders
        self.scene.factory.ctx.physics.create_ladder(x=1.5, y=2, height=4)
        self.scene.factory.ctx.physics.create_ladder(x=8.5, y=1, height=5)
        self.scene.factory.ctx.physics.create_ladder(x=2.5, y=6, height=5)

        self.editor_ui = editor.SceneEditor(engine.buffer, self.scene.factory)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.scene.factory.players.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        self.editor_ui.update()

        # --- Demo Camera movement -------------------------------------------------------------------------------------
        """
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.manager.camera.move_ip(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.manager.camera.move_ip(1, 0)
        if keys[pygame.K_UP]:
            self.manager.camera.move_ip(0, 1)
        if keys[pygame.K_DOWN]:
            self.manager.camera.move_ip(0, -1)
        """

        player_char_actor = self.scene.factory.ctx.players.actors[0]
        phys_actor = self.scene.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)
        self.scene.factory.camera.set_center(phys_actor.pos, constants.WORLD_SCALE)

        self.scene.factory.update(elapsed_ms)

        # --- Demo Enemy Ai --------------------------------------------------------------------------------------------
        # FIXME: enemies.py for further implementations, maybe reuse parts of the player controls code here

        # --- Demo: limit pos to screen --------------------------------------------------------------------------------
        for player in self.scene.factory.ctx.players.actors:
            phys_actor = self.scene.factory.ctx.physics.actors.get_by_id(player.object_id)
            if phys_actor.pos.y < 0:
                phys_actor.pos.y += constants.RESOLUTION_Y // constants.WORLD_SCALE

    def draw(self) -> None:
        self.scene.factory.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, constants.RESOLUTION_Y - fps_surface.get_height()))

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()
