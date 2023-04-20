import pygame
from typing import Optional

from core import constants, resources, state_machine

from platformer import animations, characters
from platformer import factory
from platformer import controls, physics

from . import files


class PreviewState(state_machine.State, factory.EventListener):
    def __init__(self, engine: state_machine.Engine, src: physics.Context, pos: pygame.math.Vector2):
        super().__init__(engine)
        self.cache = resources.Cache()
        self.font = self.cache.get_font()

        generic_guy = self.cache.get_sprite_sheet('guy')
        blue_guy = self.cache.get_hsl_transformed(generic_guy, resources.HslTransform(hue=216),
                                                  constants.SPRITE_CLOTHES_COLORS)

        self.factory = factory.Factory(self, self.cache, engine.buffer)
        player_char_actor = self.factory.create_character(sprite_sheet=blue_guy, x=pos.x, y=pos.y, max_hit_points=5,
                                                          num_axes=10)
        self.factory.create_player(player_char_actor,
                                   keys=controls.Keybinding(left_key=pygame.K_a, right_key=pygame.K_d,
                                                            up_key=pygame.K_w, down_key=pygame.K_s,
                                                            attack_key=pygame.K_SPACE))

        files.apply_context(self.factory.ctx.physics, src)

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

        self.factory.players.process_event(event)

    def update(self, elapsed_ms: int) -> None:
        player_char_actor = self.factory.ctx.players.actors[0]
        phys_actor = self.factory.ctx.physics.actors.get_by_id(player_char_actor.object_id)
        self.factory.camera.set_center(phys_actor.pos, constants.WORLD_SCALE)

        self.factory.update(elapsed_ms)

    def draw(self) -> None:
        self.factory.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, constants.RESOLUTION_Y - fps_surface.get_height()))
