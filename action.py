import pygame
import math
import imgui

from core import constants, resources

from platformer import animations, physics, factory, editor

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
        self.manager = factory.ObjectManager(self.cache, engine.buffer)
        player_char_actor = self.manager.create_character(sprite_sheet=blue_guy, x=2, y=5, max_hit_points=5, num_axes=10)
        self.manager.create_player(player_char_actor, left_key=pygame.K_a, right_key=pygame.K_d, up_key=pygame.K_w,
                                   down_key=pygame.K_s, attack_key=pygame.K_SPACE)

        phys_actor = self.manager.physics_context.actors.get_by_id(player_char_actor.object_id)
        #self.manager.camera.follow.append(phys_actor)

        # --- create demo scene ---------------------------------------------------------------------------------------
        self.manager.create_character(sprite_sheet=grey_guy, x=6.5, y=6.5, max_hit_points=2, num_axes=0)
        self.manager.create_character(sprite_sheet=grey_guy, x=6.5, y=4.5, max_hit_points=2, num_axes=0)

        # horizontal platforms
        self.manager.physics_context.create_platform(x=1, y=1, width=3, height=1)
        self.manager.physics_context.create_platform(x=1, y=6, width=3)
        self.manager.physics_context.create_platform(x=7, y=2, width=3, height=2)
        self.manager.physics_context.create_platform(x=2, y=2, width=2)
        self.manager.physics_context.create_platform(x=0, y=4, width=3)
        self.manager.physics_context.create_platform(x=6, y=1, width=3)
        for i in range(100):
            self.manager.physics_context.create_platform(x=10 + i, y=0, width=1, height=1 + i)
        self.manager.physics_context.create_platform(x=5, y=6, width=4)

        self.manager.physics_context.create_platform(x=3, y=7, width=1, hover=physics.Hovering(x=math.cos, amplitude=-2))

        self.manager.physics_context.create_platform(x=1, y=11, width=12)

        self.manager.create_random_object()
        self.manager.physics_context.create_object(x=1, y=1, object_type=constants.ObjectType.FOOD)

        # ladders
        self.manager.physics_context.create_ladder(x=1.5, y=2, height=4)
        self.manager.physics_context.create_ladder(x=8.5, y=1, height=5)
        self.manager.physics_context.create_ladder(x=2.5, y=6, height=5)

        self.editor_ui = editor.SceneEditor(engine.buffer, self.manager)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and \
                pygame.key.get_mods() & pygame.KMOD_ALT:
            # FIXME: pygame.display.toggle_fullscreen() does not work correctly when leaving fullscreen
            pass

        self.manager.controls.process_event(event)

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

        player_char_actor = self.manager.controls_context.actors[0]
        phys_actor = self.manager.physics_context.actors.get_by_id(player_char_actor.object_id)
        self.manager.camera.set_center(phys_actor.pos, constants.WORLD_SCALE)

        self.manager.update(elapsed_ms)

        # --- Demo Enemy Ai --------------------------------------------------------------------------------------------
        for enemy in self.manager.characters_context.actors:
            if self.manager.controls_context.actors.get_by_id(enemy.object_id) is not None:
                # ignore players
                continue

            ani_enemy = self.manager.animations_context.actors.get_by_id(enemy.object_id)
            if ani_enemy.frame.action in [animations.Action.DIE, animations.Action.ATTACK, animations.Action.THROW,
                                          animations.Action.LANDING]:
                continue

            phys_enemy = self.manager.physics_context.actors.get_by_id(enemy.object_id)
            if phys_enemy.on_platform is None:
                continue

            left_bound = phys_enemy.on_platform.pos.x + phys_enemy.on_platform.width * 0.05
            right_bound = phys_enemy.on_platform.pos.x + phys_enemy.on_platform.width * 0.95
            if phys_enemy.pos.x < left_bound:
                phys_enemy.move.face_x = 1.0
            elif phys_enemy.pos.x > right_bound:
                phys_enemy.move.face_x = -1.0

            phys_enemy.move.force.x = phys_enemy.move.face_x
            ani_enemy.frame.start(animations.Action.MOVE)

        # --- Demo: limit pos to screen --------------------------------------------------------------------------------
        for player in self.manager.controls_context.actors:
            phys_actor = self.manager.physics_context.actors.get_by_id(player.object_id)
            phys_actor.pos.x = max(0.0, min(phys_actor.pos.x, constants.RESOLUTION_X / constants.WORLD_SCALE))
            if phys_actor.pos.y < 0:
                phys_actor.pos.y += constants.RESOLUTION_Y // constants.WORLD_SCALE

    def draw(self) -> None:
        self.manager.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, constants.RESOLUTION_Y - fps_surface.get_height()))

        # draw imgui UI
        imgui.new_frame()
        self.editor_ui.draw()
        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()
