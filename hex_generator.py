#!/usr/bin/env python3
import argparse
from collections import namedtuple
import math
from svgwrite import Drawing

Hexagon = namedtuple('Hex', 'vertices position')


def generate_hexagonal_board(radius=2):
    """
    Creates a board with hexagonal shape.

    The board includes all the field within radius from center of the board.
    Setting radius to 0 generates a board with 1 hexagon.
    """
    def hex_distance(a, b): return int(abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) / 2

    width = height = 2 * radius + 1
    board = [[0] * height for _ in range(width)]
    center = (radius, radius)

    for x in range(width):
        for y in range(height):
            board[x][y] = int(hex_distance((x, y), center) <= radius)
    return board


def generate_triangular_board(edge=7, mirrored=False):
    """
    Creates a board with a shape of equilateral triangle.

    The size of the triangle's side (in fields) is specified by the edge argument.
    By default the resulting board will be a triangle pointing down (pointy top)
    of right (flat top). Setting mirrored to True changes this to a triangle
    pointing up or left, respectively.
    """
    def is_field(x, y): return x + y < edge if not mirrored else x + y + 1 >= edge
    board = [[int(is_field(x, y)) for y in range(edge)] for x in range(edge)]
    return board


def generate_parallelogrammatic_board(width=5, height=5):
    """
    Creates a board with a shape of a parallelogram.

    Width and height specify the size (in fields) of the board.
    """
    return [[1] * height for _ in range(width)]


def write_board_to_text_file(board, file_name):
    """
    Saves a board to a text file of given name.

    If the board is not a rectangle, missing fields will be filled with 0.
    """
    max_len = max(len(column) for column in board)
    for column in board:
        while len(column) < max_len:
            column.append(0)
    board = [list(row) for row in zip(*board)]
    with open(file_name, 'w') as board_file:
        for row in board:
            line = ' '.join(str(field) for field in row)
            board_file.write(line + '\n')


def read_board_from_text_file(file_name):
    """
    Reads a board from a text file of given name.

    If the file does not contain a rectangular board, missing
    fields will be filled with 0.
    """
    with open(file_name) as board_file:
        lines = board_file.readlines()
    board = [[int(x) for x in line.split()] for line in lines]
    max_len = max(len(row) for row in board)
    for row in board:
        while len(row) < max_len:
            row.append(0)
    board = [list(x) for x in zip(*board)]
    return board
        

def write_board_to_svg_file(board, file_name, hex_edge=50, hex_offset=0,
                            board_padding=None, pointy_top=True, trim_board=True, style=None):
    """
    Writes given board to a svg file of given name.

    :param board: 2 dimensional list of fields, each represented as a number
    :param file_name name of the output file
    :param hex_edge: length of hexagon's side (in pixels)
    :param hex_offset: distance between side of one hexagon and its neighbour (in pixels)
    :param board_padding padding of the board (in pixels)
    :param pointy_top: specifies if hexagons should be pointy topped or flat topped
    :param trim_board: if True, fields with a value 0 will be removed during transformation
    :param style css style (as string)
    """
    if board_padding is None:
        board_padding = hex_edge

    styles = ['.board { fill: white } .hex-field { fill: white; stroke: black } .hex-field-0 { fill: black }']
    if style is not None:
        styles.append(style)

    hexagons = transform_board_into_hexagons(board, hex_edge, hex_offset, pointy_top, trim_board)
    min_x, min_y, max_x, max_y = calculate_bounding_box(hexagons)
    offset = (board_padding - min_x, board_padding - min_y)
    hexagons = move_hexagons_by_offset(hexagons, offset)

    board_size = (2 * board_padding + max_x - min_x, 2 * board_padding + max_y - min_y)

    svg_image = create_svg_image(styles, board_size, hexagons)
    svg_image.saveas(file_name, pretty=True)
    return svg_image


def transform_board_into_hexagons(board, hex_edge, hex_offset, pointy_top=True, trim_board=True):
    """
    Converts a board to a list of  hexagons.

    :param board: 2 dimensional list of fields, each represented as a number
    :param hex_edge: length of hexagon's side
    :param hex_offset: distance between side of one hexagon and its neighbour
    :param pointy_top: specifies if hexagons should be pointy topped or flat topped
    :param trim_board: if True, fields with a value 0 will be removed during transformation
    :return: list of hexagons, each as a tuple (vertices, type)
    """
    hexagons = []
    x_axis, y_axis = create_axis(pointy_top)
    scale = hex_edge * math.sqrt(3) + hex_offset
    for x in range(len(board)):
        for y in range(len(board[x])):
            if not board[x][y] and trim_board:
                continue
            coord_x = (x_axis[0] * x + y_axis[0] * y) * scale
            coord_y = (x_axis[1] * x + y_axis[1] * y) * scale
            hex_center = (coord_x, coord_y)
            vertices = calculate_vertices_for_one_hexagon((0, 0), hex_edge, pointy_top)
            hexagons.append(Hexagon(vertices, hex_center))
    return hexagons


def create_axis(pointy_top):
    """
    Creates 2 axes (X and Y) for axial coordinate system.

    The angle between both axes is 60 degrees. Each axis has a length of 1.
    Depending on pointy_top setting, there are 2 possible sets of axes:
    * X axis pointing right (as standard cartesian X axis), Y axis rotated
    30 degrees anti-clockwise from its normal position
    * Y axis pointing down (as standard cartesian Y axis), X axis rotated 30 degrees clockwise from its normal position
    :param pointy_top: if True, X axis will point right, otherwise Y axis will point down
    :return: a tuple of 2 vectors (X, Y), each containing x and y coordinates of one axis
    """
    x_angle = 0 if pointy_top else 30
    y_angle = x_angle + 60
    x_axis = (math.cos(math.radians(x_angle)), math.sin(math.radians(x_angle)))
    y_axis = (math.cos(math.radians(y_angle)), math.sin(math.radians(y_angle)))
    return x_axis, y_axis


def calculate_vertices_for_one_hexagon(center, edge, pointy_top):
    """
    Calculates the vertices (corners) of one hexagon.

    :param center: center point of a hexagon as a tuple (x, y)
    :param edge: size of a hexagon edge
    :param pointy_top: if True, hexagon will be oriented horizontally, otherwise vertically
    :return: list of vertices for a given hexagon
    """
    vertices = []
    x, y = center
    start_angle = 0 if pointy_top else 30
    for i in range(6):
        angle = start_angle + (360 * i / 6)
        radian = math.radians(angle)
        vertex_x = x + edge * math.sin(radian)
        vertex_y = y + edge * math.cos(radian)
        vertices.append((vertex_x, vertex_y))
    return vertices


def calculate_bounding_box(hexagons):
    """
    Calculates the dimensions on a minimal bounding box (MBB) for given hexagons.

    MBB is the smallest rectangle that all given objects can fit into.
    :param hexagons iterable of hexagons (tuples in a form of (vertices, type) )
    :returns MBB as a tuple (min_x, min_y, max_x, max_y)
    """
    vertices = [
        tuple(sum(c) for c in zip(vertex, hexagon.position))
        for hexagon in hexagons for vertex in hexagon.vertices
    ]
    min_x = min(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_x = max(v[0] for v in vertices)
    max_y = max(v[1] for v in vertices)
    return min_x, min_y, max_x, max_y


def move_hexagons_by_offset(hexagons, offset):
    """
    Adds given offset to each vertex in each given hexagon.

    :param hexagons iterable of hexagons (tuples in a form of (vertices, type) )
    :param offset offset in a form of a tuple (x_offset, y_offset)
    :returns new list of hexagons, with modifies vertices
    """
    moved_hexagons = []
    for hexagon in hexagons:
        position = (
            hexagon.position[0] + offset[0], hexagon.position[1] + offset[1]
        )
        moved_hexagons.append(Hexagon(hexagon.vertices, position))
    return moved_hexagons


def create_svg_image(styles, board_size, hexagons):
    """
    Creates SVG drawing.

    The drawing contains all given css styles, a board (background rectangle)
    of given size and all given hexagons. The board can be styled using '.board'.
    All hexagonal fields can be styled using '.hex-field'. Fields can be also
    styled using 'hex-field-X', where X is the type of the field.
    :param styles iterable of css styles (strings)
    :param board_size tuple representing board size (width, height)
    :param hexagons iterable of hexagons (tuples in a form of (vertices, type) )
    :returns SVG Drawing object
    """
    svg_image = Drawing(viewBox=" ".join(str(i) for i in (0, 0) + board_size))
    for i, hexagon in enumerate(hexagons):
        group = svg_image.g(id_="hex-group-{}".format(i))
        group.translate(*hexagon.position)
        group.add(svg_image.polygon(
            hexagon.vertices, class_="hex-field", id_="hex-field-{}".format(i)
        ))
        svg_image.add(group)
    return svg_image


def main():
    """
    Creates an argument parser and handles command line execution of this program.
    """
    parser = argparse.ArgumentParser(description='Generate a board with hexagonal fields (as SVG file).')
    parser.add_argument('-o', '--output', help='name of the output file')
    parser.add_argument('-E', '--export', action='store_true',
                        help='instead of generating SVG file, the program will generate text file with a board')

    board_options = parser.add_argument_group('Board options')
    board_options.add_argument('-i', '--input', help='name of the text file with a board (overrides other options)')
    board_options.add_argument('-t', '--type', help='type of the board', choices=['hex', 'par', 'tri'], default='hex')
    board_options.add_argument('-R', '--radius', type=int, default=2, help='radius (hexagonal board)')
    board_options.add_argument('-W', '--width', type=int, default=5, help='width (parallelogrammatic board)')
    board_options.add_argument('-H', '--height', type=int, default=5, help='height (parallelogrammatic board)')
    board_options.add_argument('-S', '--size', type=int, default=7, help='edge size (triangular board)')
    board_options.add_argument('-M', '--mirrored', action='store_true', help='mirrors the board (triangular board)')

    svg_options = parser.add_argument_group('SVG options')
    svg_options.add_argument('-e', '--edge', type=int, default=50, help='length (in pixels) of hex edge')
    svg_options.add_argument('-s', '--spacing', type=int, default=0, help='spacing (in pixels) between hexes')
    svg_options.add_argument('-p', '--padding', type=int, help='board padding (in pixels)')
    svg_options.add_argument('-f', '--flat-top', action='store_true', help='changes hex orientation to vertical')
    svg_options.add_argument('-a', '--all', action='store_true', help='show all fields, including 0')
    svg_options.add_argument('-c', '--css', help='a string containing a css style to be applied to the svg file. '
                                                 'Background can be styled using ".board". Fields can be styled using '
                                                 '".hex-field" (all fields) and .hex-field-X (fields of type X).')

    args = parser.parse_args()

    if args.input:
        board = read_board_from_text_file(args.input)
    elif args.type == 'par':
        board = generate_parallelogrammatic_board(args.width, args.height)
    elif args.type == 'tri':
        board = generate_triangular_board(args.size, args.mirrored)
    else:
        board = generate_hexagonal_board(args.radius)

    if args.export:
        output_file_name = args.output if args.output else 'board.txt'
        write_board_to_text_file(board, output_file_name)
    else:
        output_file_name = args.output if args.output else 'board.svg'
        write_board_to_svg_file(board, output_file_name, args.edge, args.spacing, args.padding, not args.flat_top,
                                not args.all, args.css)

if __name__ == '__main__':
    main()
