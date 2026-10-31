#!/usr/bin/env python3
"""Generate matching Gazebo Classic SDF and Nav2 PGM map from one layout."""

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RESOLUTION = 0.05
ORIGIN_X, ORIGIN_Y = -6.5, -4.5
WIDTH, HEIGHT = 260, 180


@dataclass(frozen=True)
class Box:
    name: str
    x: float
    y: float
    width: float
    depth: float
    height: float
    rgb: tuple[float, float, float]


# Everything here is static. Coordinates are in metres in Gazebo's world frame.
# The default robot spawn (-4.6, -2.4) and tested goal (4.4, 1.5) are clear.
BOXES = (
    Box('north_wall', 0, 4, 12.2, .2, 1, (.40, .43, .47)),
    Box('south_wall', 0, -4, 12.2, .2, 1, (.40, .43, .47)),
    Box('east_wall', 6, 0, .2, 8.2, 1, (.40, .43, .47)),
    Box('west_wall', -6, 0, .2, 8.2, 1, (.40, .43, .47)),
    Box('shelf_west_north', -1.7, 1.6, .8, 1.7, .7, (.12, .38, .68)),
    Box('shelf_west_south', -1.7, -1.6, .8, 1.7, .7, (.12, .38, .68)),
    Box('shelf_east_north', 1.6, 1.6, .8, 1.7, .7, (.12, .38, .68)),
    Box('shelf_east_south', 1.6, -1.6, .8, 1.7, .7, (.12, .38, .68)),
    Box('crate_centre', 0, 0, .85, .85, .55, (.70, .35, .09)),
    Box('crate_east', 3.6, 0, 1, 1, .55, (.70, .35, .09)),
)


def add_box(world: ET.Element, box: Box) -> None:
    model = ET.SubElement(world, 'model', name=box.name)
    ET.SubElement(model, 'static').text = 'true'
    ET.SubElement(model, 'pose').text = f'{box.x} {box.y} {box.height / 2} 0 0 0'
    link = ET.SubElement(model, 'link', name='link')
    size = f'{box.width} {box.depth} {box.height}'
    for kind in ('collision', 'visual'):
        part = ET.SubElement(link, kind, name=kind)
        ET.SubElement(ET.SubElement(ET.SubElement(part, 'geometry'), 'box'), 'size').text = size
        if kind == 'visual':
            material = ET.SubElement(part, 'material')
            rgba = ' '.join(str(v) for v in (*box.rgb, 1))
            ET.SubElement(material, 'ambient').text = rgba
            ET.SubElement(material, 'diffuse').text = rgba


def write_world(path: Path) -> None:
    sdf = ET.Element('sdf', version='1.6')
    world = ET.SubElement(sdf, 'world', name='warehouse_demo')
    ET.SubElement(world, 'gravity').text = '0 0 -9.8'
    light = ET.SubElement(world, 'light', name='sun', type='directional')
    ET.SubElement(light, 'pose').text = '0 0 10 0 0 0'
    ET.SubElement(light, 'diffuse').text = '0.85 0.85 0.85 1'
    ET.SubElement(light, 'specular').text = '0.2 0.2 0.2 1'
    ET.SubElement(light, 'direction').text = '-0.3 -0.4 -1'
    floor = ET.SubElement(world, 'model', name='floor')
    ET.SubElement(floor, 'static').text = 'true'
    link = ET.SubElement(floor, 'link', name='link')
    for kind in ('collision', 'visual'):
        part = ET.SubElement(link, kind, name=kind)
        geometry = ET.SubElement(part, 'geometry')
        plane = ET.SubElement(geometry, 'plane')
        ET.SubElement(plane, 'normal').text = '0 0 1'
        ET.SubElement(plane, 'size').text = '20 20'
        if kind == 'visual':
            material = ET.SubElement(part, 'material')
            ET.SubElement(material, 'ambient').text = '0.7 0.7 0.7 1'
            ET.SubElement(material, 'diffuse').text = '0.7 0.7 0.7 1'
    for box in BOXES:
        add_box(world, box)
    ET.indent(sdf, space='  ')
    ET.ElementTree(sdf).write(path, encoding='utf-8', xml_declaration=True)


def write_map(pgm: Path, yaml: Path) -> None:
    # PGM rows start at the *top* of the image; map origin is bottom left.
    pixels = bytearray()
    for row in range(HEIGHT):
        y = ORIGIN_Y + (HEIGHT - row - .5) * RESOLUTION
        for col in range(WIDTH):
            x = ORIGIN_X + (col + .5) * RESOLUTION
            occupied = any(abs(x - b.x) <= b.width / 2 and
                           abs(y - b.y) <= b.depth / 2 for b in BOXES)
            inside = -5.9 < x < 5.9 and -3.9 < y < 3.9
            pixels.append(0 if occupied else 254 if inside else 128)
    pgm.write_bytes(f'P5\n{WIDTH} {HEIGHT}\n255\n'.encode() + pixels)
    yaml.write_text(
        f'image: {pgm.name}\nmode: trinary\nresolution: {RESOLUTION}\n'
        f'origin: [{ORIGIN_X}, {ORIGIN_Y}, 0.0]\nnegate: 0\n'
        'occupied_thresh: 0.65\nfree_thresh: 0.25\n', encoding='utf-8')


if __name__ == '__main__':
    (ROOT / 'worlds').mkdir(exist_ok=True)
    (ROOT / 'maps').mkdir(exist_ok=True)
    write_world(ROOT / 'worlds' / 'warehouse.world')
    write_map(ROOT / 'maps' / 'warehouse.pgm', ROOT / 'maps' / 'warehouse.yaml')
    print('Generated worlds/warehouse.world and maps/warehouse.{pgm,yaml}')
