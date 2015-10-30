import argparse
from collections import namedtuple
import math
from svgwrite import Drawing

Hexagon = namedtuple('Hex', 'vertices type')


def generate_hexagonal_board(radius=2):
    def hex_distance(a, b): return int(abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[0] + a[1] - b[0] - b[1])) / 2

    width = height = 2 * radius + 1
    board = [[0] * height for _ in range(width)]
    center = (radius, radius)

    for x in range(width):
        for y in range(height):
            board[x][y] = int(hex_distance((x, y), center) <= radius)
    return board


def generate_triangular_board(edge=7, upper=True):
    def is_field(x, y): return x + y < edge if upper else x + y + 1 >= edge
    board = [[int(is_field(x, y)) for y in range(edge)] for x in range(edge)]
    return board


def generate_rhomboidal_board(width=5, height=5):
    return [[1] * height for _ in range(width)]


def write_board_to_text_file(board, file_name):
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
    svg_image.saveas(file_name)
    return svg_image


def transform_board_into_hexagons(board, hex_edge, hex_offset, pointy_top=True, trim_board=True):
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
            vertices = calculate_vertices_for_one_hexagon(hex_center, hex_edge, pointy_top)
            hexagons.append(Hexagon(vertices, board[x][y]))
    return hexagons


def create_axis(pointy_top):
    x_angle = 0 if pointy_top else 30
    y_angle = x_angle + 60
    x_axis = (math.cos(math.radians(x_angle)), math.sin(math.radians(x_angle)))
    y_axis = (math.cos(math.radians(y_angle)), math.sin(math.radians(y_angle)))
    return x_axis, y_axis


def calculate_vertices_for_one_hexagon(center, edge, pointy_top):
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
    vertices = [vertex for hexagon in hexagons for vertex in hexagon.vertices]
    min_x = min(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_x = max(v[0] for v in vertices)
    max_y = max(v[1] for v in vertices)
    return min_x, min_y, max_x, max_y


def move_hexagons_by_offset(hexagons, offset):
    moved_hexagons = []
    for hexagon in hexagons:
        vertices = [(v[0] + offset[0], v[1] + offset[1]) for v in hexagon.vertices]
        moved_hexagons.append(Hexagon(vertices, hexagon.type))
    return moved_hexagons


def create_svg_image(styles, board_size, hexagons):
    svg_image = Drawing()
    for style in styles:
        svg_image.add(svg_image.style(style))
    svg_image.add(svg_image.rect(size=board_size, class_='board'))
    for hexagon in hexagons:
        svg_image.add(svg_image.polygon(hexagon.vertices, class_='hex-field hex-field-%d' % hexagon.type))
    return svg_image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output', help='name of the output file')
    parser.add_argument('-E', '--export', action='store_true',
                        help='instead of generating SVG file, the program will generate text file with a board')

    board_options = parser.add_argument_group('Board options')
    board_options.add_argument('-i', '--input', help='name of the text file with a board (overrides other options)')
    board_options.add_argument('-t', '--type', help='type of the board', choices=['hex', 'rho', 'tri'], default='hex')
    # board_options.add_argument('-r', '--radius', type=int, default=2, help='radius (of hexagonal board)')
    # board_options.add_argument('-w', '--width', type=int, default=5, help='width (of rhomboidal board)')
    # # board_options.add_argument('-h', '--height', type=int, default=5, help='height (of rhomboidal board)')
    # board_options.add_argument('-x', '--xxx', help='xxx (of triangular board)')

    svg_options = parser.add_argument_group('SVG options')
    svg_options.add_argument('-e', '--edge', type=int, default=50, help='length (in pixels) of hex edge')
    svg_options.add_argument('-a', '--all', action='store_true', help='show all fields, including 0')
    svg_options.add_argument('-c', '--css', help='css style to be applied to the svg board')
    svg_options.add_argument('-f', '--flat-top', action='store_true', help='changes hex orientation to vertical')
    svg_options.add_argument('-p', '--padding', type=int, help='board padding (in pixels)')
    svg_options.add_argument('-s', '--spacing', type=int, default=0, help='spacing (in pixels) between hexes')

    args = parser.parse_args()

    if args.input:
        board = read_board_from_text_file(args.input)
    elif args.type == 'rho':
        board = generate_rhomboidal_board()
    elif args.type == 'tri':
        board = generate_triangular_board()
    else:
        board = generate_hexagonal_board()

    if args.export:
        output_file_name = args.output if args.output else 'board.txt'
        write_board_to_text_file(board, output_file_name)
    else:
        output_file_name = args.output if args.output else 'board.svg'
        write_board_to_svg_file(board, output_file_name, args.edge, args.spacing, args.padding, not args.flat_top,
                                not args.all, args.css)

if __name__ == '__main__':
    main()
