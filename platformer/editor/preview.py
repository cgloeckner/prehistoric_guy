import pygame
from typing import Optional

from core import constants, resources, state_machine

from platformer import physics, animations, renderer, characters, controls, factory

from . import files


class PreviewState(state_machine.State, factory.EventListener):
    def __init__(self, engine: state_machine.Engine, src: physics.Context, pos: pygame.math.Vector2):
        super().__init__(engine)
        self.cache = resources.Cache()
        self.font = self.cache.get_font()

        # create minimal systems
        self.physics_ctx = physics.Context()
        self.animations_ctx = animations.Context()
        self.renderer_ctx = renderer.Context()
        self.players_ctx = controls.PlayersContext()

        self.physics = physics.System(self, self.physics_ctx)
        self.animations = animations.AnimationSystem(self, self.animations_ctx, self.physics_ctx)
        self.camera = renderer.Camera(*engine.buffer.get_size())
        self.renderer = renderer.Renderer(self.camera, engine.buffer, self.physics_ctx, self.animations_ctx,
                                          self.renderer_ctx, self.cache)
        self.players = controls.PlayersSystem(self.players_ctx, self.physics_ctx, self.animations_ctx)

        # load level
        files.apply_context(self.physics_ctx, src)

        # create player
        generic_guy = self.cache.get_sprite_sheet('guy')
        self.physics_ctx.create_actor(1, x=pos.x, y=pos.y)
        self.animations_ctx.create_actor(1)
        self.renderer_ctx.create_actor(1, sprite_sheet=generic_guy)
        player = self.players_ctx.create_actor(1)
        player.keys = controls.Keybinding(left_key=pygame.K_a, right_key=pygame.K_d, up_key=pygame.K_w,
                                          down_key=pygame.K_s, attack_key=pygame.K_SPACE)

    # ------------------------------------------------------------------------------------------------------------------

    def on_grab(self, actor: physics.Actor) -> None:
        pass

    def on_release(self, actor: physics.Actor) -> None:
        pass

    def on_falling(self, phys_actor: physics.Actor) -> None:
        pass

    def on_landing(self, phys_actor: physics.Actor) -> None:
        pass

    def on_collision(self, actor: physics.Actor, platform: physics.Platform) -> None:
        pass

    def on_touch_object(self, phys_actor: physics.Actor, obj: physics.Object) -> None:
        pass

    def on_impact_platform(self, proj: physics.Projectile, platform: physics.Platform) -> None:
        pass

    def on_impact_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        pass

    def on_touch_actor(self, proj: physics.Projectile, phys_actor: physics.Actor) -> None:
        pass

    def on_climb(self, ani: animations.Actor) -> None:
        pass

    def on_step(self, ani: animations.Actor) -> None:
        pass

    def on_attack(self, ani: animations.Actor) -> None:
        pass

    def on_throw(self, ani_actor: animations.Actor) -> None:
        pass

    def on_died(self, ani_actor: animations.Actor) -> None:
        pass

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        pass

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        pass

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        self.players.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        # let camera follow player
        phys_actor = self.physics_ctx.actors.get_by_id(1)
        self.camera.set_center(phys_actor.pos, constants.WORLD_SCALE)

        self.physics.update(elapsed_ms)
        self.animations.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.players.update(elapsed_ms)

    def draw(self) -> None:
        self.renderer.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, constants.RESOLUTION_Y - fps_surface.get_height()))
