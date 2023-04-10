import pygame
import math
import imgui

from core.constants import *
from core import resources

from platformer import animations
from platformer import physics
from platformer import factory
from platformer import editor

import state_machine


class GameState(state_machine.State):
    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.cache = resources.Cache()

        # --- loading some resources ----------------------------------------------------------------------------------
        self.font = self.cache.get_font()
        generic_guy = self.cache.get_sprite_sheet('guy')
        blue_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(hue=0.6),
                                                  SPRITE_CLOTHES_COLORS)
        grey_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(saturation=0.0),
                                                  SPRITE_CLOTHES_COLORS)

        # --- setup object manager with player character ---------------------------------------------------------------
        self.manager = factory.ObjectManager(self.cache, engine.buffer)
        player_char_actor = self.manager.create_character(sprite_sheet=blue_guy, x=2, y=5)
        self.manager.create_player(player_char_actor, left_key=pygame.K_a, right_key=pygame.K_d, up_key=pygame.K_w,
                                   down_key=pygame.K_s, attack_key=pygame.K_SPACE)

        # --- create demo scene ---------------------------------------------------------------------------------------
        self.manager.create_character(sprite_sheet=grey_guy, x=6.5, y=6.5)
        self.manager.create_character(sprite_sheet=grey_guy, x=6.5, y=4.5)

        # horizontal platforms
        self.manager.create_platform(x=0, y=1, width=3, height=2)
        self.manager.create_platform(x=2, y=2, width=2)
        self.manager.create_platform(x=0, y=4, width=3)
        self.manager.create_platform(x=6, y=1, width=3)
        self.manager.create_platform(x=4, y=4, width=1, height=11)
        self.manager.create_platform(x=5, y=6, width=4)

        self.manager.create_platform(x=3, y=6, width=1, hover=physics.Hovering(x=math.cos, amplitude=-2))

        # ladders
        self.manager.create_ladder(x=1, y=1, height=7)
        self.manager.create_ladder(x=8, y=1, height=5)

        self.manager.create_random_object()

        self.editor_ui = editor.SceneEditor(engine.buffer, self.manager)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.manager.players.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        self.editor_ui.update()

        # --- Demo Camera movement -------------------------------------------------------------------------------------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.manager.renderer.move_camera(-1, 0)
        if keys[pygame.K_RIGHT]:
            self.manager.renderer.move_camera(1, 0)
        if keys[pygame.K_UP]:
            self.manager.renderer.move_camera(0, 1)
        if keys[pygame.K_DOWN]:
            self.manager.renderer.move_camera(0, -1)

        self.manager.update(elapsed_ms)

        # # --- Demo Enemy Ai ------------------------------------------------------------------------------------------
        for enemy in self.manager.chars.characters:
            if self.manager.players.try_get_by_id(enemy.object_id) is not None:
                # ignore players
                continue

            ani_enemy = self.manager.animation.get_by_id(enemy.object_id)
            if ani_enemy.action_id in [animations.DIE_ACTION, animations.ATTACK_ACTION,
                                       animations.THROW_ACTION, animations.LANDING_ACTION]:
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
            animations.start(ani_enemy, animations.MOVE_ACTION)

        # --- Demo: limit pos to screen --------------------------------------------------------------------------------
        for player in self.manager.players.players:
            phys_actor = self.manager.physics.get_by_id(player.object_id)
            phys_actor.x = max(0.0, min(phys_actor.x, RESOLUTION_X / WORLD_SCALE))
            if phys_actor.y < 0:
                phys_actor.y += RESOLUTION_Y // WORLD_SCALE

    def draw(self) -> None:
        self.manager.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, RESOLUTION_Y - fps_surface.get_height()))

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()
