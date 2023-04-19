import xml.dom.minidom
import xml.etree.ElementTree as et

from typing import List

from core import constants

from platformer import physics


class Scene:
    def __init__(self, ctx: physics.Context):
        self.ctx = ctx
        self.player_ids: List[int] = list()
        self.filename: str = ''

    @staticmethod
    def from_xml(root: et.Element) -> 'Scene':
        """Creates a new scene from a dictionary."""
        scene = Scene(physics.Context())

        for child in root:
            x = float(child.attrib['x'])
            y = float(child.attrib['y'])

            if child.tag == 'platform':
                width = int(child.attrib['width'])
                height = int(child.attrib['height']) if 'height' in child.attrib else 0
                scene.ctx.create_platform(x=x, y=y, width=width, height=height)

            elif child.tag == 'ladder':
                height = int(child.attrib['height'])
                scene.ctx.create_ladder(x=x, y=y, height=height)

            elif child.tag == 'object':
                # read from all caps name
                object_type = constants.ObjectType.__members__[child.attrib['object_type'].upper()]
                scene.ctx.create_object(x=x, y=y, object_type=object_type)

        return scene

    def to_xml(self) -> et.Element:
        """Collects all data as a dictionary."""
        root = et.Element('level')

        for platform in self.ctx.platforms:
            elem = et.SubElement(root, 'platform')
            elem.set('x', str(platform.pos.x))
            elem.set('y', str(platform.pos.y))
            elem.set('width', str(platform.width))
            if platform.height > 0:
                elem.set('height', str(platform.height))

        for ladder in self.ctx.ladders:
            elem = et.SubElement(root, 'ladder')
            elem.set('x', str(ladder.pos.x))
            elem.set('y', str(ladder.pos.y))
            elem.set('height', str(ladder.height))

        for obj in self.ctx.objects:
            elem = et.SubElement(root, 'object')
            elem.set('x', str(obj.pos.x))
            elem.set('y', str(obj.pos.y))
            elem.set('object_type', obj.object_type.name)

        return root

    def to_file(self, filename: str = ''):
        root = self.to_xml()
        dump = et.tostring(root, encoding='unicode', xml_declaration=False, method="xml")

        # indent xml string
        dom = xml.dom.minidom.parseString(dump)
        dump = dom.toprettyxml()

        with open(filename, 'w') as file:
            file.write(dump)

    @staticmethod
    def from_file(filename: str) -> 'Scene':
        tree = et.parse(filename)
        return Scene.from_xml(tree.getroot())


if __name__ == '__main__':
    context = physics.Context()
    context.create_platform(x=2.0, y=1.0, width=4, height=0)
    context.create_platform(x=4.0, y=0.0, width=3, height=1)
    context.create_ladder(x=1.5, y=2, height=4)

    #s = Scene(context)
    s = Scene.from_file('../data/level001.xml')
    s.to_file('/tmp/level001.xml')


