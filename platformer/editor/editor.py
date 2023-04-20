import pygame
import imgui
from typing import List

from core import state_machine, resources
from platformer import physics, animations, renderer

from . import files


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

        self.font = self.cache.get_font()
        self.new_filename = ''
        self.file_status = files.FileStatus()

        # DEMO
        self.file_status.filename = 'level01'
        self.on_level_load()

    def get_level_files(self) -> List[str]:
        path = self.engine.paths.levels()
        return [file.stem for file in path.glob('*.xml') if file.is_file()]

    def process_event(self, event: pygame.event.Event) -> None:
        was_eaten = False

        if event.type == pygame.QUIT:
            self.engine.pop()

        if not was_eaten:
            self.engine.wrapper.process_event(event)

    def on_level_new(self) -> None:
        self.file_status.filename = ''
        self.file_status.unsaved_changes = True

        # replace platforms, ladders and objects
        self.physics_context.platforms.clear()
        self.physics_context.ladders.clear()
        self.physics_context.objects.clear()

        # reset camera
        self.camera.topleft = pygame.math.Vector2()

    def on_level_load(self) -> None:
        self.file_status.unsaved_changes = False
        full_path = self.engine.paths.levels(self.file_status.filename)

        ctx = files.from_xml(files.from_file(full_path))

        # replace platforms, ladders and objects
        self.physics_context.platforms = ctx.platforms
        self.physics_context.ladders = ctx.ladders
        self.physics_context.objects = ctx.objects

        # reset camera
        self.camera.topleft = pygame.math.Vector2()

    def on_level_save(self) -> None:
        self.file_status.unsaved_changes = False

        full_path = self.engine.paths.levels(self.file_status.filename)
        print('save', full_path)

    def on_level_quit(self) -> None:
        if self.file_status.unsaved_changes:
            print('FIXME: warning popup')

        self.engine.pop()

    def on_level_run(self) -> None:
        pass

    def main_menu(self) -> None:
        menu_action = ''

        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                with imgui.begin_menu('File') as file_menu:
                    if file_menu.opened:
                        if imgui.menu_item('New')[0]:
                            self.on_level_new()
                        if imgui.menu_item('Open')[0]:
                            menu_action = 'open'
                        imgui.new_line()
                        if imgui.menu_item('Save')[0]:
                            menu_action = 'save'
                        if imgui.menu_item('Save as')[0]:
                            menu_action = 'save-as'
                        imgui.new_line()
                        if imgui.menu_item('Quit')[0]:
                            self.on_level_quit()
                with imgui.begin_menu('Level') as level_menu:
                    if level_menu.opened:
                        if imgui.menu_item('Run')[0]:
                            self.on_level_run()

                imgui.same_line(150)
                imgui.text(f'POS  {self.camera.topleft}  ')
                imgui.text(f'LEVEL  {self.file_status}  ')

        # NOTE: popups need to be opened AFTER the main menu
        if menu_action == 'open':
            imgui.open_popup('Load Level')

        elif menu_action == 'save':
            if self.file_status.filename == '':
                self.new_filename = self.file_status.get_filename()
                imgui.open_popup('Save Level')
            else:
                self.on_level_save()

        elif menu_action == 'save-as':
            self.new_filename = self.file_status.get_filename()
            imgui.open_popup('Save Level')

    def setup_popup(self) -> None:
        max_width, max_height = self.engine.screen_size
        w = max(400, max_width * 0.8)
        h = max(300, max_height * 0.8)
        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(max_width // 2 - w // 2, max_height // 2 - h // 2)

    def load_popup(self):
        level_files = self.get_level_files()
        self.setup_popup()
        with imgui.begin_popup_modal('Load Level') as open_popup:
            if open_popup.opened:
                imgui.text('Select Level File:')
                imgui.same_line(400)
                if imgui.button('Cancel'):
                    imgui.close_current_popup()

                imgui.separator()
                imgui.columns(3, 'filelist', False)
                for index, filename in enumerate(level_files):
                    if imgui.selectable(filename)[1]:
                        self.file_status.filename = filename
                        self.on_level_load()
                    imgui.next_column()

    def save_popup(self):
        level_files = self.get_level_files()
        self.setup_popup()
        with imgui.begin_popup_modal('Save Level') as open_popup:
            if open_popup.opened:
                imgui.text('File Name')
                imgui.same_line()
                imgui.push_item_width(300)
                _, self.new_filename = imgui.input_text('', self.new_filename)

                if len(self.new_filename) > 0 and self.new_filename not in level_files:
                    imgui.same_line()
                    if imgui.button('Create'):
                        self.file_status.filename = self.new_filename
                        self.on_level_save()
                        imgui.close_current_popup()

                imgui.same_line()
                if imgui.button('Cancel'):
                    imgui.close_current_popup()

                imgui.text('Or Select Level File:')

                imgui.separator()
                imgui.columns(3, 'filelist', False)
                for index, filename in enumerate(level_files):
                    if imgui.selectable(filename)[1]:
                        self.file_status.filename = filename
                        self.on_level_save()
                    imgui.next_column()

    def update(self, elapsed_ms: int) -> None:
        self.renderer.update(elapsed_ms)

        if not self.engine.wrapper.io.want_capture_keyboard:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.camera.topleft.x -= 0.01 * elapsed_ms
            if keys[pygame.K_RIGHT]:
                self.camera.topleft.x += 0.01 * elapsed_ms
            if keys[pygame.K_UP]:
                self.camera.topleft.y += 0.01 * elapsed_ms
            if keys[pygame.K_DOWN]:
                self.camera.topleft.y -= 0.01 * elapsed_ms

    def draw(self) -> None:
        self.renderer.draw()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, self.engine.screen_size[1] - fps_surface.get_height()))

        # draw imgui
        imgui.new_frame()

        self.main_menu()
        self.load_popup()
        self.save_popup()

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