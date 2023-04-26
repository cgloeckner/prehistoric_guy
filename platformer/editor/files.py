import pathlib
import xml.dom.minidom
import xml.etree.ElementTree as et
from dataclasses import dataclass
from typing import List

from core import constants, paths

from platformer import physics


@dataclass
class FileStatus:
    filename: str = ''
    unsaved_changes: bool = False

    def get_filename(self) -> str:
        if self.filename == '':
            return 'untitled'
        return self.filename

    def __str__(self) -> str:
        suffix = ' [UNSAVED]' if self.unsaved_changes else ''
        return self.get_filename() + suffix


def apply_context(target: physics.Context, tmp: physics.Context):
    # replace platforms, ladders and objects
    target.platforms = tmp.platforms
    target.ladders = tmp.ladders
    target.objects = tmp.objects


def to_xml(ctx: physics.Context) -> et.Element:
    """Collects relevant as a dictionary."""
    root = et.Element('level')

    for platform in ctx.platforms:
        elem = et.SubElement(root, 'platform')
        elem.set('x', str(platform.pos.x))
        elem.set('y', str(platform.pos.y))
        if hasattr(platform, 'original_pos'):
            elem.set('x', str(platform.original_pos.x))
            elem.set('y', str(platform.original_pos.y))
        elem.set('width', str(platform.width))
        if platform.height > 0:
            elem.set('height', str(platform.height))
        if platform.hover.x != physics.HoverType.NONE:
            elem.set('hover_x', platform.hover.x.name.lower())
        if platform.hover.y != physics.HoverType.NONE:
            elem.set('hover_y', platform.hover.y.name.lower())
        if platform.hover.amplitude != 1.0:
            elem.set('amplitude', str(platform.hover.amplitude))

    for ladder in ctx.ladders:
        elem = et.SubElement(root, 'ladder')
        elem.set('x', str(ladder.pos.x))
        elem.set('y', str(ladder.pos.y))
        elem.set('height', str(ladder.height))

    for obj in ctx.objects:
        elem = et.SubElement(root, 'object')
        elem.set('x', str(obj.pos.x))
        elem.set('y', str(obj.pos.y))
        elem.set('object_type', obj.object_type.name.lower())

    return root


def from_xml(root: et.Element) -> physics.Context:
    """Creates a new scene from a dictionary."""
    ctx = physics.Context()

    for child in root:
        x = float(child.attrib['x'])
        y = float(child.attrib['y'])

        if child.tag == 'platform':
            width = int(child.attrib['width'])
            height = int(child.attrib['height']) if 'height' in child.attrib else 0
            p = ctx.create_platform(x=x, y=y, width=width, height=height)
            p.original_pos = p.pos.copy()
            if 'hover_x' in child.attrib:
                p.hover.x = physics.HoverType.__members__[child.attrib['hover_x'].upper()]
            if 'hover_y' in child.attrib:
                p.hover.y = physics.HoverType.__members__[child.attrib['hover_y'].upper()]
            p.hover.amplitude = float(child.attrib['amplitude']) if 'amplitude' in child.attrib else 1.0

        elif child.tag == 'ladder':
            height = int(child.attrib['height'])
            ctx.create_ladder(x=x, y=y, height=height)

        elif child.tag == 'object':
            # read from all caps name
            object_type = constants.ObjectType.__members__[child.attrib['object_type'].upper()]
            ctx.create_object(x=x, y=y, object_type=object_type)

    return ctx


def to_file(root: et.Element, path: pathlib.Path) -> None:
    dump = et.tostring(root, encoding='unicode', xml_declaration=False, method="xml")

    # indent xml string
    dom = xml.dom.minidom.parseString(dump)
    dump = dom.toprettyxml()

    with open(path, 'w') as file:
        file.write(dump)


def from_file(path: pathlib.Path) -> et.Element:
    return et.parse(path).getroot()


def get_level_files(path: pathlib.Path) -> List[str]:
    """Returns a list of all level files."""
    return paths.DataPath.get_files(path, 'xml')


def load_level(path: pathlib.Path, target: physics.Context) -> None:
    tmp = from_xml(from_file(path))
    apply_context(target, tmp)
