import pygame
from typing import Optional

from core import constants, resources, state_machine

from platformer import physics, animations, renderer, characters, controls, factory

from . import files


class PreviewState(state_machine.State, factory.EventListener):
    def __init__(self, engine: state_machine.Engine, src: physics.Context, pos: pygame.math.Vector2,
                 tileset_index: int):
        super().__init__(engine)
        self.cache = resources.Cache(engine.paths)
        self.font = self.cache.get_font()

        # create minimal systems
        self.physics_ctx = physics.Context()
        self.animations_ctx = animations.Context()
        self.renderer_ctx = renderer.Context()
        self.players_ctx = controls.PlayersContext()

        self.physics = physics.System(self, self.physics_ctx)
        self.animations = animations.AnimationSystem(self, self.animations_ctx, self.physics_ctx)
        self.camera = renderer.Camera()
        self.renderer = renderer.Renderer(self.camera, engine.buffer, self.physics_ctx, self.animations_ctx,
                                          self.renderer_ctx, self.cache)
        self.renderer.load_fileset(tileset_index)
        self.parallax = renderer.ParallaxRenderer(self.camera, engine.buffer, self.cache)

        self.players = controls.PlayersSystem(self.players_ctx, self.physics_ctx, self.animations_ctx)

        self.engine.fill_color = self.parallax.get_fill_color()

        # load level
        files.apply_context(self.physics_ctx, src)

        # create player
        guy_path = self.engine.paths.sprite('guy')
        generic_guy = self.cache.get_sprite_sheet(guy_path)
        self.physics_ctx.create_actor(1, x=pos.x, y=pos.y)
        self.animations_ctx.create_actor(1)
        self.renderer_ctx.create_actor(1, sprite_sheet=generic_guy)
        self.players_ctx.create_actor(1)

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

    def on_animation_finish(self, ani_actor: animations.Actor) -> None:
        pass

    def on_char_damaged(self, actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        pass

    def on_char_died(self, char_actor: characters.Actor, damage: int, cause: Optional[characters.Actor]) -> None:
        pass

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

    def update(self, elapsed_ms: int) -> None:
        # let camera follow player
        phys_actor = self.physics_ctx.actors.get_by_id(1)
        self.camera.set_center_x(phys_actor.pos.x)

        self.physics.update(elapsed_ms)
        self.animations.update(elapsed_ms)
        self.parallax.update(elapsed_ms)
        self.renderer.update(elapsed_ms)
        self.players.update(elapsed_ms)

    def draw(self) -> None:
        self.parallax.draw()
        self.renderer.draw()

        pygame.display.set_caption(f'Preview - {int(self.engine.num_fps):02d} FPS')
