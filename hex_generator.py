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
        

def write_board_to_svg_file(board, file_name, hex_radius=50, hex_offset=0, board_padding=None, pointy_top=True, trim_board=True, css=None):
    if board_padding is None:
        board_padding = hex_radius

    styles = ['.background { fill: white } '
              '.hex-field { fill: white; stroke-width: 1; stroke: black } '
              '.hex-field-0 { fill: black }']
    if css is not None:
        styles.append(css)

    hexagons = get_hexes(board, hex_radius, hex_offset, pointy_top, trim_board)
    all_vertices = [v for hexagon in hexagons for v in hexagon.vertices]
    min_x = min(v[0] for v in all_vertices)
    min_y = min(v[1] for v in all_vertices)
    max_x = max(v[0] for v in all_vertices)
    max_y = max(v[1] for v in all_vertices)
    x_offset = board_padding - min_x
    y_offset = board_padding - min_y

    board_width = 2 * board_padding + (max_x - min_x)
    board_height = 2 * board_padding + (max_y - min_y)
    size=(board_width, board_height)

    new_hexagons = []
    for hexagon in hexagons:
        vertices = [(v[0] + x_offset, v[1] + y_offset) for v in hexagon.vertices]
        new_hexagons.append(Hexagon(vertices, hexagon.type))
    hexagons = new_hexagons

    svg_image = create_svg(styles, size, hexagons)
    svg_image.saveas(file_name)
    return svg_image


def create_svg(styles, size, hexagons):
    svg_image = Drawing()
    for style in styles:
        svg_image.add(svg_image.style(style))
    svg_image.add(svg_image.rect(size=size, class_='background'))
    for hexagon in hexagons:
        svg_image.add(svg_image.polygon(hexagon.vertices, class_='hex-field hex-field-%d' % hexagon.type))
    return svg_image


def get_hexes(board, hex_radius, hex_offset, pointy_top, trim_board=True):
    hexes = []
    x_angle = 0 if pointy_top else 30
    y_angle = x_angle + 60
    x_axis = (math.cos(x_angle * math.pi / 180.0), math.sin(x_angle * math.pi / 180.0))
    y_axis = (math.cos(y_angle * math.pi / 180.0), math.sin(y_angle * math.pi / 180.0))
    scale = hex_radius * math.sqrt(3) + hex_offset
    for x in range(len(board)):
        for y in range(len(board[x])):
            if not board[x][y] and trim_board:
                continue
            coord_x = (x_axis[0] * x + y_axis[0] * y) * scale
            coord_y = (x_axis[1] * x + y_axis[1] * y) * scale
            coordinates = (coord_x, coord_y)
            vertices = calculate_one_hex_vertices(coordinates, hex_radius, pointy_top)
            hexes.append(Hexagon(vertices, board[x][y]))

    return hexes


def calculate_one_hex_vertices(coordinates, hex_radius, pointy_top):
    vertices = []
    x, y = coordinates
    start_angle = 0 if pointy_top else 30
    for i in range(6):
        angle = start_angle + (360 * i / 6)
        radian = angle * math.pi / 180.
        px = x + hex_radius * math.sin(radian)
        py = y + hex_radius * math.cos(radian)
        vertices.append((px, py))
    return vertices


if __name__ == "__main__":
    simple_board = generate_hexagonal_board()
    write_board_to_svg_file(simple_board, 'board.svg', css='.background { fill: navy} .hex-field-1 { fill: yellow}')
