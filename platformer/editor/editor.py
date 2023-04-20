import pygame
import imgui
import pathlib
from typing import List

from core import state_machine, resources, paths, shapes
from platformer import physics, animations, renderer

from . import files, preview


MOUSE_SELECT_RADIUS: float = 0.2


class LevelSelection:
    def __init__(self):
        self.platforms: List[physics.Platform] = list()
        self.ladders: List[physics.Ladder] = list()
        self.objects: List[physics.Object] = list()

    def clear(self) -> None:
        self.platforms.clear()
        self.ladders.clear()
        self.objects.clear()


# ----------------------------------------------------------------------------------------------------------------------


class Context:
    def __init__(self, width: int, height: int, p: paths.DataPath):
        self.new_filename = ''
        self.file_status = files.FileStatus()
        self.ctx = physics.Context()
        self.cam = renderer.Camera(width, height)
        self.paths = p

        self.selected = LevelSelection()
        self.hovered = LevelSelection()

        self.reset()

    def reset(self):
        self.file_status.filename = ''
        self.file_status.unsaved_changes = True

        # replace platforms, ladders and objects
        self.ctx.platforms.clear()
        self.ctx.ladders.clear()
        self.ctx.objects.clear()
        self.ctx.create_platform(x=0, y=0, width=10)

        # reset camera
        self.cam.topleft = pygame.math.Vector2(-1, -1)

    def load(self):
        self.file_status.unsaved_changes = False
        full_path = self.get_full_levelname()
        ctx = files.from_xml(files.from_file(full_path))

        files.apply_context(self.ctx, ctx)

        # reset camera
        self.cam.topleft = pygame.math.Vector2()

    def save(self):
        self.file_status.unsaved_changes = False
        full_path = self.get_full_levelname()
        files.to_file(files.to_xml(self.ctx), full_path)

    def get_full_levelname(self) -> pathlib.Path:
        return self.paths.level(self.file_status.filename)


# ----------------------------------------------------------------------------------------------------------------------


class EditorState(state_machine.State):

    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.context = Context(*engine.buffer.get_size(), engine.paths)

        self.engine.translate.load_from_file(self.engine.paths.language('en'))

        self.cache = resources.Cache()
        self.animations_context = animations.Context()
        self.sprite_context = renderer.Context()
        self.renderer = renderer.Renderer(self.context.cam, engine.buffer, self.context.ctx, self.animations_context,
                                          self.sprite_context, self.cache)

        self.font = self.cache.get_font()

    def get_level_files(self) -> List[str]:
        path = self.engine.paths.level()
        return sorted([file.stem for file in path.glob('*.xml') if file.is_file()])

    def get_mouse_pos(self) -> pygame.math.Vector2:
        pos = pygame.math.Vector2(pygame.mouse.get_pos())
        return self.renderer.to_world_coord(pos)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.engine.pop()

    def on_level_new(self) -> None:
        self.context.reset()

    def on_level_load(self) -> None:
        self.context.load()

    def on_level_save(self) -> None:
        self.context.save()

    def on_level_quit(self) -> None:
        if self.context.file_status.unsaved_changes:
            print('FIXME: warning popup')

        self.engine.pop()

    def on_level_run(self) -> None:
        player_pos = pygame.math.Vector2(5, 5)
        self.engine.push(preview.PreviewState(self.engine, self.context.ctx, player_pos))

    def main_menu(self) -> None:
        ui = self.engine.translate
        menu_action = ''

        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                with imgui.begin_menu(ui.editor.level) as file_menu:
                    if file_menu.opened:
                        if imgui.menu_item(ui.editor.new)[0]:
                            self.on_level_new()
                        if imgui.menu_item(ui.editor.open)[0]:
                            menu_action = 'open'
                        imgui.new_line()
                        if imgui.menu_item(ui.editor.save)[0]:
                            menu_action = 'save'
                        if imgui.menu_item(ui.editor.save_as)[0]:
                            menu_action = 'save-as'
                        imgui.new_line()
                        if imgui.menu_item(ui.editor.quit)[0]:
                            self.on_level_quit()
                if imgui.menu_item(ui.editor.run)[0]:
                    self.on_level_run()

                imgui.same_line(200)
                if imgui.menu_item(f'{ui.editor.filename}: {self.context.file_status}')[0]:
                    menu_action = 'open'

        with imgui.begin(ui.editor.status):
            # camera position
            imgui.text(f'{ui.editor.cam} {self.context.cam.topleft}')

            # mouse position
            mouse_pos = self.get_mouse_pos()
            mouse_pos_str = f'[{mouse_pos.x:.2f}, {mouse_pos.y:.2f}]'
            imgui.text(f'{ui.editor.mouse} {mouse_pos_str}')

        # NOTE: popups need to be opened AFTER the main menu
        if menu_action == 'open':
            imgui.open_popup(ui.editor.open)

        elif menu_action == 'save':
            if self.context.file_status.filename == '':
                self.context.new_filename = self.context.file_status.get_filename()
                imgui.open_popup(ui.editor.save)
            else:
                self.on_level_save()

        elif menu_action == 'save-as':
            self.context.new_filename = self.context.file_status.get_filename()
            imgui.open_popup(ui.editor.save)

    def setup_popup(self) -> None:
        max_width, max_height = self.engine.screen_size
        w = max(400, max_width * 0.8)
        h = max(300, max_height * 0.8)
        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(max_width // 2 - w // 2, max_height // 2 - h // 2)

    def load_popup(self):
        ui = self.engine.translate

        level_files = self.get_level_files()
        self.setup_popup()
        with imgui.begin_popup_modal(ui.editor.open) as open_popup:
            if open_popup.opened:
                imgui.text(ui.editor.select_level)
                imgui.same_line(400)
                if imgui.button(ui.editor.cancel):
                    imgui.close_current_popup()

                imgui.separator()
                imgui.columns(3, ui.editor.filelist, False)
                for index, filename in enumerate(level_files):
                    if imgui.selectable(filename)[1]:
                        self.context.file_status.filename = filename
                        self.on_level_load()
                    imgui.next_column()

    def save_popup(self):
        ui = self.engine.translate

        level_files = self.get_level_files()
        self.setup_popup()
        with imgui.begin_popup_modal(ui.editor.save) as open_popup:
            if open_popup.opened:
                imgui.text(ui.editor.filename)
                imgui.same_line()
                imgui.push_item_width(300)
                _, self.context.new_filename = imgui.input_text('', self.context.new_filename)

                if len(self.context.new_filename) > 0 and self.context.new_filename not in level_files:
                    imgui.same_line()
                    if imgui.button(ui.editor.create):
                        self.context.file_status.filename = self.context.new_filename
                        self.on_level_save()
                        imgui.close_current_popup()

                imgui.same_line()
                if imgui.button(ui.editor.cancel):
                    imgui.close_current_popup()

                imgui.text(ui.editor.select_level)

                imgui.separator()
                imgui.columns(3, ui.editor.filelist, False)
                for index, filename in enumerate(level_files):
                    if imgui.selectable(filename)[1]:
                        self.context.file_status.filename = filename
                        self.on_level_save()
                    imgui.next_column()

    def update_cam_move(self, elapsed_ms: int) -> None:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.context.cam.topleft.x -= 0.01 * elapsed_ms
        if keys[pygame.K_RIGHT]:
            self.context.cam.topleft.x += 0.01 * elapsed_ms
        if keys[pygame.K_UP]:
            self.context.cam.topleft.y += 0.01 * elapsed_ms
        if keys[pygame.K_DOWN]:
            self.context.cam.topleft.y -= 0.01 * elapsed_ms

    def update_mouse_hover(self):
        pos = self.get_mouse_pos()

        self.context.hovered.clear()
        src = self.context.ctx
        circ = shapes.Circ(*pos, MOUSE_SELECT_RADIUS)

        def mouse_over_platform(platform: physics.Platform) -> bool:
            return platform.contains_point(pos) or circ.collideline(platform.get_line())

        self.context.hovered.platforms = [platform for platform in src.platforms if mouse_over_platform(platform)]
        self.context.hovered.ladders = [ladder for ladder in src.ladders if ladder.is_in_reach_of(pos)]
        self.context.hovered.objects = [obj for obj in src.objects if obj.get_circ().collidecirc(circ)]

    def update(self, elapsed_ms: int) -> None:
        self.renderer.update(elapsed_ms)

        if not self.engine.wrapper.io.want_capture_keyboard:
            self.update_cam_move(elapsed_ms)

        if not self.engine.wrapper.io.want_capture_mouse:
            self.update_mouse_hover()

    def draw(self) -> None:
        self.renderer.draw()

        # redraw hovered objects
        for platform in self.context.hovered.platforms:
            self.renderer.draw_platform(platform, use_mask=True)
        for ladder in self.context.hovered.ladders:
            self.renderer.draw_ladder(ladder, use_mask=True)
        for obj in self.context.hovered.objects:
            self.renderer.draw_object(obj, use_mask=True)

        # draw imgui
        self.main_menu()
        self.load_popup()
        self.save_popup()

        # draw FPS
        fps_surface = self.font.render(f'FPS: {int(self.engine.num_fps):02d}', False, 'white')
        self.engine.buffer.blit(fps_surface, (0, self.engine.screen_size[1] - fps_surface.get_height()))



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