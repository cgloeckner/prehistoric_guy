import pygame
import imgui

from core import constants, state_machine, resources
from platformer import animations, renderer

from . import preview, context, files


class EditorState(state_machine.State, animations.EventListener):

    def __init__(self, engine: state_machine.Engine):
        super().__init__(engine)
        self.context = context.Context(*engine.buffer.get_size(), engine.paths, engine.translate)

        self.engine.translate.load_from_file(self.engine.paths.language('en'))

        self.cache = resources.Cache(engine.paths)
        self.animations_context = animations.Context()
        self.sprite_context = renderer.Context()
        self.animations = animations.AnimationSystem(self, self.animations_context, self.context.ctx)
        self.renderer = renderer.Renderer(self.context.cam, engine.buffer, self.context.ctx, self.animations_context,
                                          self.sprite_context, self.cache)

        self.parallax = renderer.ParallaxRenderer(self.context.cam, engine.buffer, self.cache)

        self.font = self.cache.get_font()
        self.quit = False
        self.engine.fill_color = self.parallax.get_fill_color()

    def __del__(self):
        pass

    def reinit(self) -> None:
        # pygame.event.set_grab(True)
        pass

    def sleep(self) -> None:
        # pygame.event.set_grab(False)
        pass

    # --- required to initialize animations system (for platform hovering) ---------------------------------------------

    def on_step(self, ani: animations.Actor) -> None: ...
    def on_climb(self, ani: animations.Actor) -> None: ...
    def on_attack(self, ani: animations.Actor) -> None: ...
    def on_throw(self, ani: animations.Actor) -> None: ...
    def on_died(self, ani: animations.Actor) -> None: ...

    # ------------------------------------------------------------------------------------------------------------------

    def main_menu(self) -> None:
        """Handles the main menu with click events."""
        ui = self.engine.translate
        menu_action = ''

        with imgui.begin_main_menu_bar() as main_menu_bar:
            if main_menu_bar.opened:
                # level: new, open, save, save-as, quit
                with imgui.begin_menu(ui.editor.level) as file_menu:
                    if file_menu.opened:
                        if imgui.menu_item(ui.editor.new)[0]:
                            self.on_level_new()
                        if imgui.menu_item(ui.editor.load)[0]:
                            menu_action = 'open'
                        imgui.new_line()
                        if imgui.menu_item(ui.editor.save)[0]:
                            menu_action = 'save'
                        if imgui.menu_item(ui.editor.save_as)[0]:
                            menu_action = 'save-as'
                        imgui.new_line()
                        if imgui.menu_item(ui.editor.quit + ' (ESC)')[0]:
                            menu_action = 'quit'

                # tool menu: mode, snap, run
                with imgui.begin_menu(ui.editor.tools) as tools_menu:
                    if tools_menu.opened:
                        with imgui.begin_menu(ui.editor.mode) as mode_menu:
                            if mode_menu.opened:
                                for value in context.EditorMode:
                                    if imgui.radio_button(getattr(ui.editor, value.name.lower()),
                                                          self.context.mode == value):
                                        self.context.mode = value

                        with imgui.begin_menu(ui.editor.tileset) as tileset_menu:
                            if tileset_menu.opened:
                                all_tiles = self.engine.paths.all_tiles()
                                for index, value in enumerate(all_tiles):
                                    if imgui.menu_item(getattr(ui.editor, value))[0]:
                                        self.context.tileset_index = index
                                        self.renderer.load_fileset(index)

                        _, self.context.snap_enabled = imgui.checkbox(ui.editor.snap, self.context.snap_enabled)

                        if imgui.menu_item(ui.editor.run + ' (F5)')[0]:
                            self.on_level_run()

                imgui.same_line(200)
                if imgui.menu_item(str(self.context.file_status))[0]:
                    menu_action = 'open'

        # NOTE: popups need to be opened AFTER the main menu
        if menu_action == 'open':
            imgui.open_popup(ui.editor.load)

        elif menu_action == 'save':
            if self.context.file_status.filename == '':
                self.context.new_filename = self.context.file_status.get_filename()
                imgui.open_popup(ui.editor.save)
            else:
                self.on_level_save()

        elif menu_action == 'save-as':
            self.context.new_filename = self.context.file_status.get_filename()
            imgui.open_popup(ui.editor.save)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_F5]:
            self.on_level_run()

        if keys[pygame.K_ESCAPE] or menu_action == 'quit' or self.quit:
            self.quit = False
            ui = self.engine.translate

            if self.context.file_status.unsaved_changes:
                imgui.open_popup(ui.editor.discard)
            else:
                imgui.open_popup(ui.editor.leave)

    # ------------------------------------------------------------------------------------------------------------------

    def setup_large_popup(self) -> None:
        """Sets up a large popup to be centered."""
        max_width, max_height = self.engine.get_opengl_size()
        w = max(constants.RESOLUTION_X, int(max_width * 0.8))
        h = max(constants.RESOLUTION_Y, int(max_height * 0.8))
        imgui.set_next_window_size(w, h)

    def popups(self):
        """Handles all popups with click events."""
        ui = self.engine.translate
        level_files = files.get_level_files(self.engine.paths.level())

        next_popup = ''

        self.setup_large_popup()
        with imgui.begin_popup_modal(ui.editor.load) as open_popup:
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

                        if self.context.file_status.unsaved_changes:
                            next_popup = ui.editor.discard_load
                        else:
                            self.on_level_load()

                    imgui.next_column()

        if next_popup != '':
            imgui.open_popup(next_popup)

        self.setup_large_popup()
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

        max_width, max_height = self.engine.get_opengl_size()
        w = 200
        h = 100

        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(max_width // 2 - w // 2, max_height // 2 - h // 2)
        with imgui.begin_popup_modal(ui.editor.discard) as discard_popup:
            if discard_popup.opened:
                imgui.text_wrapped(ui.editor.discard_message)
                if imgui.button(ui.editor.discard):
                    self.engine.pop()

                imgui.same_line()
                if imgui.button(ui.editor.cancel):
                    imgui.close_current_popup()

        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(max_width // 2 - w // 2, max_height // 2 - h // 2)
        with imgui.begin_popup_modal(ui.editor.leave) as leave_popup:
            if leave_popup.opened:
                imgui.text_wrapped(ui.editor.leave_message)
                if imgui.button(ui.editor.leave):
                    self.engine.pop()

                imgui.same_line()
                if imgui.button(ui.editor.cancel):
                    imgui.close_current_popup()

        imgui.set_next_window_size(w, h)
        imgui.set_next_window_position(max_width // 2 - w // 2, max_height // 2 - h // 2)
        with imgui.begin_popup_modal(ui.editor.discard_load) as leave_popup:
            if leave_popup.opened:
                imgui.text_wrapped(ui.editor.discard_message)
                if imgui.button(ui.editor.load):
                    self.on_level_load()
                    imgui.close_current_popup()

                imgui.same_line()
                if imgui.button(ui.editor.cancel):
                    imgui.close_current_popup()

    # ------------------------------------------------------------------------------------------------------------------

    def process_event(self, event: pygame.event.Event) -> None:
        """Handles pygame events."""
        if event.type == pygame.QUIT:
            self.quit = True

        if not self.engine.wrapper.io.want_capture_mouse:
            if event.type == pygame.MOUSEWHEEL:
                self.context.on_wheel(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.context.on_left_click(event)
                elif event.button == 3:
                    self.context.on_right_click(event)

        if not self.engine.wrapper.io.want_capture_keyboard:
            if event.type == pygame.KEYDOWN:
                self.context.on_key_pressed(event.key)

    def on_level_new(self) -> None:
        """Callback for creating a new level."""
        self.context.reset()

    def on_level_load(self) -> None:
        """Callback for loading a level."""
        self.context.load()

    def on_level_save(self) -> None:
        """Callback for saving a level."""
        self.context.save()

    def on_level_run(self) -> None:
        """Callback for preview running a level."""
        player_pos = pygame.math.Vector2(5, 5)
        self.engine.push(preview.PreviewState(self.engine, self.context.ctx, player_pos, self.context.tileset_index))

    def update_cam_move(self, elapsed_ms: int) -> None:
        """Handles the camera movement."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.context.cam.topleft.x -= 0.01 * elapsed_ms
        if keys[pygame.K_RIGHT]:
            self.context.cam.topleft.x += 0.01 * elapsed_ms

    def update(self, elapsed_ms: int) -> None:
        """Update various things."""
        self.animations.update(elapsed_ms)
        self.parallax.update(elapsed_ms)
        self.renderer.update(elapsed_ms)

        if not self.engine.wrapper.io.want_capture_keyboard:
            self.update_cam_move(elapsed_ms)

        if not self.engine.wrapper.io.want_capture_mouse:
            pos = pygame.math.Vector2(pygame.mouse.get_pos())
            self.context.mouse_pos = self.renderer.to_world_coord(pos)

            self.context.update_mouse(elapsed_ms)

        self.context.update(elapsed_ms)

        # handle imgui
        self.main_menu()
        self.popups()

    def draw(self) -> None:
        """Draw scene and things the like."""
        self.parallax.draw()
        self.renderer.draw()
        self.context.draw(self.renderer)
