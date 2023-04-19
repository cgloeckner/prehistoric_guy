import pathlib
import xml.dom.minidom
import xml.etree.ElementTree as et

from core import constants

from platformer import physics


def to_xml(ctx: physics.Context) -> et.Element:
    """Collects relevant as a dictionary."""
    root = et.Element('level')

    for platform in ctx.platforms:
        elem = et.SubElement(root, 'platform')
        elem.set('x', str(platform.pos.x))
        elem.set('y', str(platform.pos.y))
        elem.set('width', str(platform.width))
        if platform.height > 0:
            elem.set('height', str(platform.height))

    for ladder in ctx.ladders:
        elem = et.SubElement(root, 'ladder')
        elem.set('x', str(ladder.pos.x))
        elem.set('y', str(ladder.pos.y))
        elem.set('height', str(ladder.height))

    for obj in ctx.objects:
        elem = et.SubElement(root, 'object')
        elem.set('x', str(obj.pos.x))
        elem.set('y', str(obj.pos.y))
        elem.set('object_type', obj.object_type.name)

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
            ctx.create_platform(x=x, y=y, width=width, height=height)

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
