import pygame
import imgui

from core import state_machine, resources
from platformer import physics, animations, renderer


MOUSE_SELECT_RADIUS: float = 0.2


class EditorState(state_machine.State):

    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.camera = renderer.Camera(*engine.buffer.get_size())
        self.cache = resources.Cache()

        self.physics_context = physics.Context()
        self.animations_context = animations.Context()
        self.sprite_context = renderer.Context()

        self.renderer = renderer.Renderer(self.camera, engine.buffer, self.physics_context, self.animations_context,
                                          self.sprite_context, self.cache)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            self.engine.pop()

        self.engine.wrapper.process_event(event)

    def on_level_new(self) -> None:
        pass

    def on_level_open(self) -> None:
        pass

    def on_level_save(self) -> None:
        pass

    def on_level_save_as(self) -> None:
        pass

    def on_level_quit(self) -> None:
        pass

    def on_level_run(self) -> None:
        pass

    def update(self, elapsed_ms: int) -> None:
        self.renderer.update(elapsed_ms)

    def main_menu(self):
        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                with imgui.begin_menu('File') as file_menu:
                    if file_menu.opened:
                        if imgui.menu_item('New')[0]:
                            self.on_level_new()
                        if imgui.menu_item('Open')[0]:
                            self.on_level_open()
                        imgui.new_line()
                        if imgui.menu_item('Save')[0]:
                            self.on_level_save()
                        if imgui.menu_item('Save as')[0]:
                            self.on_level_save_as()
                        imgui.new_line()
                        if imgui.menu_item('Quit')[0]:
                            self.on_level_quit()
                with imgui.begin_menu('Level') as level_menu:
                    if level_menu.opened:
                        if imgui.menu_item('Run')[0]:
                            self.on_level_run()

    def draw(self) -> None:
        self.engine.buffer.fill('#a0faf0')
        self.renderer.draw()

        imgui.new_frame()
        self.main_menu()

        self.engine.wrapper.buffer.blit(self.engine.buffer, (0, 0))
        self.engine.wrapper.render()





"""
class SceneEditor(object):
    def __init__(self, screen: pygame.Surface, factory_: factory.Factory):
        self.screen = screen
        self.factory = factory_

        self.hovered_platforms: List[physics.Platform] = list()
        self.selected_platform: Optional[physics.Platform] = None

    def update(self) -> None:
        pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        pos = self.factory.renderer.to_world_coord(pos)

        all_platforms = self.factory.ctx.physics.platforms
        self.hovered_platforms = [platform for platform in all_platforms if platform.contains_point(pos)]

        print(self.hovered_platforms)

    def draw(self) -> None:
        #if isinstance(self.selected, physics.Platform):
        #    platform_ui(self.selected)

        #if isinstance(self.selected, physics.Actor):
        #    ani_actor = self.factory.animation.get_actor_by_id(self.selected.object_id)
        #    render_actor = self.factory.renderer.get_actor_by_id(self.selected.object_id)
        #    actor_ui(self.selected, ani_actor, render_actor)

        #if isinstance(self.selected, physics.Object):
        #    object_ui(self.selected)

        #if isinstance(self.selected, physics.Ladder):
        #    ladder_ui(self.selected)
        pass

    # FIXME: find a way to access coord transform
    #def get_mouse_world_pos(self) -> pygame.math.Vector2:
    #    # transform screen coordinates to game coordinates
    #    return self.obj_manager.camera.to_world_coord(*pygame.mouse.get_pos())

    def get_hovered(self) -> List:
        return []

        # FIXME: implement get_mouse_world_pos
        #pos = self.get_mouse_world_pos()
        #circ1 = shapes.Circ(*pos, MOUSE_SELECT_RADIUS)

        # collect all hoverable objects
        #hovered = list()
        #for platform in self.obj_manager.physics_context.platforms:
        #    line = platform.get_line()
        #    if platform.contains_point(pos) or circ1.collideline(line):
        #        hovered.append(platform)

        #for actor in self.obj_manager.physics_context.actors:
        #    circ2 = actor.get_circ()
        #    if circ1.collidecirc(circ2):
        #        hovered.append(actor)

        #for obj in self.obj_manager.physics_context.objects:
        #    circ2 = obj.get_circ()
        #    if circ1.collidecirc(circ2):
        #        hovered.append(obj)

        #for ladder in self.obj_manager.physics_context.ladders:
        #    if ladder.is_in_reach_of(pos):
        #        hovered.append(ladder)

        #return hovered

    def update_hover(self) -> None:

        if self.selected is not None:
            # do not alter element hovering (coloring)
            return

        # update coloring for hovered elements
        #for elem in self.hovered_elements:
        #    elem.hsl = None
        #self.hovered_elements = self.get_hovered()
        #for elem in self.hovered_elements:
        #    print(elem)

        # select first hovered element on click
        left_click = pygame.mouse.get_pressed()[0]
        if left_click and self.selected is None and len(self.hovered_elements) > 0:
            self.selected = self.hovered_elements[0]
"""