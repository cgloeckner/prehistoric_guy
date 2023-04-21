import pygame
import pathlib
import imgui
from typing import List, Optional, Tuple
from enum import IntEnum, auto

from core import paths, shapes, constants, translate
from platformer import physics, renderer

from . import files


MOUSE_SELECT_RADIUS: float = 0.2


class EditorMode(IntEnum):
    SELECT = 0
    CREATE_PLATFORM = auto()
    CREATE_LADDER = auto()
    CREATE_OBJECT = auto()


class Context:
    def __init__(self, width: int, height: int, p: paths.DataPath, t: translate.Match):
        self.new_filename = ''
        self.file_status = files.FileStatus()
        self.ctx = physics.Context()
        self.cam = renderer.Camera(width, height)
        self.paths = p
        self.translate = t

        self.mouse_pos = pygame.math.Vector2()
        self.mode = EditorMode.SELECT
        self.snap_enabled = True

        self.preview_platform: Optional[physics.Platform] = None
        self.preview_ladder: Optional[physics.Ladder] = None
        self.preview_object: Optional[physics.Object] = None

        self.preview_terrain_size = 3
        self.preview_obj_type = constants.ObjectType.FOOD

        self.hovered_platforms: List[physics.Platform] = list()
        self.hovered_ladders: List[physics.Ladder] = list()
        self.hovered_objects: List[physics.Object] = list()

        self.selected_platform: Optional[physics.Platform] = None
        self.selected_ladder: Optional[physics.Ladder] = None
        self.selected_object: Optional[physics.Object] = None

        self.reset()

    def reset(self):
        """Resets the level to a blank one."""
        self.file_status.filename = ''
        self.file_status.unsaved_changes = True

        # replace platforms, ladders and objects
        self.ctx.platforms.clear()
        self.ctx.ladders.clear()
        self.ctx.objects.clear()

        # reset camera
        self.cam.topleft = pygame.math.Vector2(0, 0)

    def load(self):
        """Loads the level from file."""
        self.file_status.unsaved_changes = False
        full_path = self.get_full_level_name()
        ctx = files.from_xml(files.from_file(full_path))

        files.apply_context(self.ctx, ctx)

        # reset camera
        self.cam.topleft = pygame.math.Vector2(-1, -1)

    def save(self):
        """Saves the level to file."""
        self.file_status.unsaved_changes = False
        full_path = self.get_full_level_name()
        files.to_file(files.to_xml(self.ctx), full_path)

    def get_full_level_name(self) -> pathlib.Path:
        """Returns the level's full filename."""
        return self.paths.level(self.file_status.filename)

    def mouse_over_platform(self, platform: physics.Platform) -> bool:
        """"Tests whether the mouse position is at the given platform."""
        if platform.contains_point(self.mouse_pos):
            return True

        circ = shapes.Circ(*self.mouse_pos, MOUSE_SELECT_RADIUS)
        return circ.collideline(platform.get_line())

    def snap_pos(self, pos: pygame.math.Vector2) -> None:
        """Snaps the pos inplace to grid if snapping is enabled.

        Ctrl can be used to invert the snap mode setting.
        If Shift is used, an element's x never snaps but the y always snaps.
        """
        mods = pygame.key.get_mods()
        snap_x = snap_y = self.snap_enabled

        # inverse snap mode
        if mods & pygame.KMOD_CTRL > 0:
            snap_x = not snap_x
            snap_y = not snap_y

        # override snap mode
        if mods & pygame.KMOD_SHIFT > 0:
            snap_x = False
            snap_y = True

        # snap coordinates
        if snap_x:
            pos.x = int(pos.x)
        if snap_y:
            pos.y = int(pos.y)

    def on_left_click(self, event: pygame.event.Event) -> None:
        """Place previewed element."""
        if self.mode == EditorMode.CREATE_PLATFORM and self.preview_platform is not None:
            self.ctx.create_platform(x=self.preview_platform.pos.x,
                                     y=self.preview_platform.pos.y,
                                     width=self.preview_platform.width)

        elif self.mode == EditorMode.CREATE_LADDER and self.preview_ladder is not None:
            self.ctx.create_ladder(x=self.preview_ladder.pos.x,
                                   y=self.preview_ladder.pos.y,
                                   height=self.preview_ladder.height)

        elif self.mode == EditorMode.CREATE_OBJECT and self.preview_object is not None:
            self.ctx.create_object(x=self.preview_object.pos.x,
                                   y=self.preview_object.pos.y,
                                   object_type=self.preview_object.object_type)

        elif self.mode == EditorMode.SELECT:
            self.selected_platform = None
            self.selected_ladder = None
            self.selected_object = None

            # select hovered element (priority: object)
            if len(self.hovered_objects) > 0:
                self.selected_object = self.hovered_objects[0]

            elif len(self.hovered_ladders) > 0:
                self.selected_ladder = self.hovered_ladders[0]

            elif len(self.hovered_platforms) > 0:
                self.selected_platform = self.hovered_platforms[0]

    def on_right_click(self, event: pygame.event.Event) -> None:
        """Cycle editor mode."""
        new_value = (self.mode + 1) % len(EditorMode.__members__)
        self.mode = EditorMode(new_value)

    def on_wheel(self, event: pygame.event.Event) -> None:
        """Modify platform width / ladder height / object type."""
        if self.mode in [EditorMode.CREATE_PLATFORM, EditorMode.CREATE_LADDER]:
            # change platform width / ladder height (>= 1)
            self.preview_terrain_size += event.y
            if self.preview_terrain_size < 1:
                self.preview_terrain_size = 1

        elif self.mode == EditorMode.CREATE_OBJECT:
            # change object type within bounds
            new_value = (self.preview_obj_type + event.y) % len(constants.ObjectType.__members__)
            self.preview_obj_type = constants.ObjectType(new_value)

    def platform_tooltip(self, platform: physics.Platform) -> None:
        """Show platform information as tooltip."""
        with imgui.begin_tooltip():
            imgui.text(self.translate.editor.platform)
            imgui.text(f'{self.translate.editor.position}: {platform.pos}')
            imgui.text(f'{self.translate.editor.width}: {platform.width}')

    def ladder_tooltip(self, ladder: physics.Ladder) -> None:
        """Show ladder information as tooltip."""
        with imgui.begin_tooltip():
            imgui.text(self.translate.editor.ladder)
            imgui.text(f'{self.translate.editor.position}: {ladder.pos}')
            imgui.text(f'{self.translate.editor.height}: {ladder.height}')

    def object_tooltip(self, obj: physics.Object) -> None:
        """Show object information as tooltip."""
        with imgui.begin_tooltip():
            imgui.text(self.translate.editor.object)
            imgui.text(f'{self.translate.editor.position}: {obj.pos}')
            imgui.text(f'{self.translate.editor.type}: {getattr(self.translate.editor, obj.object_type.name)}')

    def position_editor(self, pos: pygame.math.Vector2) -> bool:
        changed_x, pos.x = imgui.input_float(f'{self.translate.editor.position} x', pos.x, 0.1, 1.0)
        changed_y, pos.y = imgui.input_float(f'{self.translate.editor.position} y', pos.y, 0.1, 1.0)
        return changed_x or changed_y

    def platform_editor(self) -> None:
        imgui.set_next_window_size(300, 150)
        with imgui.begin(self.translate.editor.platform):
            has_changed = self.position_editor(self.selected_platform.pos)

            changed, value = imgui.input_int(self.translate.editor.width, self.selected_platform.width, 1)
            if changed:
                if value <= 0:
                    value = 1
                self.selected_platform.width = value
                has_changed = True

            changed, value = imgui.input_int(self.translate.editor.height, self.selected_platform.height, 1)
            if changed:
                if value < 0:
                    value = 0
                self.selected_platform.height = value
                has_changed = True

            if imgui.button(self.translate.editor.delete):
                self.ctx.platforms.remove(self.selected_platform)
                self.selected_platform = None
                has_changed = True

        if has_changed:
            self.file_status.unsaved_changes = True

    def ladder_editor(self) -> None:
        imgui.set_next_window_size(300, 125)
        with imgui.begin(self.translate.editor.ladder):
            has_changed = self.position_editor(self.selected_ladder.pos)

            changed, value = imgui.input_int(self.translate.editor.height, self.selected_ladder.height, 1)
            if changed:
                if value < 0:
                    value = 0
                self.selected_ladder.height = value
                has_changed = True

            if imgui.button(self.translate.editor.delete):
                self.ctx.ladders.remove(self.selected_ladder)
                self.selected_ladder = None
                has_changed = True

        if has_changed:
            self.file_status.unsaved_changes = True

    def object_editor(self) -> None:
        imgui.set_next_window_size(300, 125)
        with imgui.begin(self.translate.editor.object):
            has_changed = self.position_editor(self.selected_object.pos)

            type_list = [value for value in constants.ObjectType.__members__]
            clicked, index = imgui.combo(self.translate.editor.type, self.selected_object.object_type, type_list)
            if clicked:
                self.selected_object.object_type = constants.ObjectType(index)
                has_changed = True

            if imgui.button(self.translate.editor.delete):
                self.ctx.objects.remove(self.selected_object)
                self.selected_object = None
                has_changed = True
        
        if has_changed:
            self.file_status.unsaved_changes = True

    def update(self, elapsed_ms: int) -> None:
        if self.mode == EditorMode.SELECT:

            if self.selected_object is not None:
                self.object_editor()

            elif self.selected_ladder is not None:
                self.ladder_editor()

            elif self.selected_platform is not None:
                self.platform_editor()

    def update_mouse(self, elapsed_ms: int) -> None:
        """Update mouse-related stuff."""
        circ = shapes.Circ(*self.mouse_pos, MOUSE_SELECT_RADIUS)

        if self.mode == EditorMode.SELECT:
            # query hovered elements
            self.hovered_platforms = [platform for platform in self.ctx.platforms if self.mouse_over_platform(platform)]
            self.hovered_ladders = [ladder for ladder in self.ctx.ladders if ladder.is_in_reach_of(self.mouse_pos)]
            self.hovered_objects = [obj for obj in self.ctx.objects if obj.get_circ().collidecirc(circ)]
            self.preview_platform = None
            self.preview_ladder = None
            self.preview_object = None

            # show next best tooltip (priority: objects)
            if len(self.hovered_objects) > 0:
                self.object_tooltip(self.hovered_objects[0])

            elif len(self.hovered_platforms) > 0:
                self.platform_tooltip(self.hovered_platforms[0])

            elif len(self.hovered_ladders) > 0:
                self.ladder_tooltip(self.hovered_ladders[0])

        else:
            self.selected_platform = None
            self.selected_ladder = None
            self.selected_object = None

            self.hovered_platforms = list()
            self.hovered_ladders = list()
            self.hovered_objects = list()

            # handle snap to grid
            pos = self.mouse_pos.copy()
            self.snap_pos(pos)

            buttons = pygame.mouse.get_pressed()
            left_click = buttons[0]

            if self.mode == EditorMode.CREATE_PLATFORM:
                self.preview_ladder = None
                self.preview_object = None
                # create/update platform
                if self.preview_platform is None:
                    self.preview_platform = physics.Platform(pos=pos.copy(), width=self.preview_terrain_size)
                else:
                    self.preview_platform.pos = pos.copy()
                    self.preview_platform.width = self.preview_terrain_size

                self.platform_tooltip(self.preview_platform)

            elif self.mode == EditorMode.CREATE_LADDER:
                self.preview_platform = None
                self.preview_object = None
                # create/update ladder
                if self.preview_ladder is None:
                    self.preview_ladder = physics.Ladder(pos=pos.copy(), height=self.preview_terrain_size)
                else:
                    self.preview_ladder.pos = pos.copy()
                    self.preview_ladder.height = self.preview_terrain_size

                self.ladder_tooltip(self.preview_ladder)

            elif self.mode == EditorMode.CREATE_OBJECT:
                self.preview_platform = None
                self.preview_ladder = None
                # create/update object
                if self.preview_object is None:
                    self.preview_object = physics.Object(pos=pos.copy(), object_type=self.preview_obj_type)
                else:
                    self.preview_object.pos = pos.copy()
                    self.preview_object.object_type = self.preview_obj_type

                self.object_tooltip(self.preview_object)

    def draw(self, render_api: renderer.Renderer) -> None:
        """Draw additional things ontop."""
        # redraw hovered objects
        for platform in self.hovered_platforms:
            render_api.draw_platform(platform, use_mask=True)
        for ladder in self.hovered_ladders:
            render_api.draw_ladder(ladder, use_mask=True)
        for obj in self.hovered_objects:
            render_api.draw_object(obj, use_mask=True)

        # redraw preview objects
        if self.preview_platform is not None:
            render_api.draw_platform(self.preview_platform)
        if self.preview_ladder is not None:
            render_api.draw_ladder(self.preview_ladder)
        if self.preview_object is not None:
            render_api.draw_object(self.preview_object)
