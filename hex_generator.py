import math
from lxml import etree


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


def generate_rectangular_board(width=5, height=5, pointy_top=False):
    if not pointy_top:
        width, height = height, width

    additional_width = int((height + 1) / 2 - 1)

    board = [[1 for y in range(height)] for x in range(width + additional_width)]

    for x in range(additional_width):
        for y in range(2 * (additional_width - x)):
            board[x][y] = 0

    for x in range(width, width + additional_width):
        for y in range(2*(width + additional_width - x), height):
            board[x][y] = 0

    if not pointy_top:
        board = zip(*board)
        board = [list(x) for x in board]

    return board


def save_board_to_file(board, file_name):
    board = zip(*board)
    with open(file_name, 'w') as board_file:
        for row in board:
            line = ' '.join(str(field) for field in row)
            board_file.write(line + '\n')


def load_board_from_file(file_name):
    with open(file_name) as f:
        lines = f.readlines()
    
    board = []    
    
    for line in lines:
        board.append([int(x) for x in line.split(' ')])
    
    board = zip(*board)
    
    return board
        

def get_intermediate_coords(board, pointy_top=False, x_scale = 1., y_scale = 1.):
    
    list_of_coords = []
    
    if pointy_top:
        x_angle = 0
    else:
        x_angle = 30
    
    y_angle = x_angle + 60
    
    x_axis = (math.cos(x_angle * math.pi / 180.0), math.sin(x_angle * math.pi / 180.0))
    y_axis = (math.cos(y_angle * math.pi / 180.0), math.sin(y_angle * math.pi / 180.0))
    
    width = len(board)
    height = len(board[0])
    
    for x in range(width):
        for y in range(height):
            if board[x][y] != 0:
                coord_x = x_axis[0]*x + y_axis[0]*y
                coord_y = x_axis[1]*x + y_axis[1]*y
                coord_x *= x_scale
                coord_y *= y_scale
                list_of_coords.append((coord_x,coord_y))
    
    return list_of_coords


def scale_coordinates(list_of_coords, hex_radius, hex_offset):
    
    scaled_coords = []
    
    scale = hex_radius*math.sqrt(3) + hex_offset
    
    for coords in list_of_coords:
        scaled_coords.append((coords[0]*scale, coords[1]*scale))
    
    return scaled_coords


def get_drawing_params(scaled_coords, hex_radius=10, board_offset=None, pointy_top=False):
    
    drawing_params = {}
    
    if board_offset == None:
        board_offset = hex_radius
        
    if pointy_top:
        radius_x = hex_radius * math.sqrt(3) * 0.5
        radius_y = hex_radius
    else:
        radius_x = hex_radius
        radius_y = hex_radius * math.sqrt(3) * 0.5
        
    min_x = min(coords[0] for coords in scaled_coords)
    max_x = max(coords[0] for coords in scaled_coords)
    min_y = min(coords[1] for coords in scaled_coords)
    max_y = max(coords[1] for coords in scaled_coords)
    
    drawing_params["width"] = (max_x - min_x) + 2 * (board_offset + radius_x)
    drawing_params["height"] = (max_y - min_y) + 2 * (board_offset + radius_y)
    drawing_params["x_offset"] = -min_x + board_offset + radius_x
    drawing_params["y_offset"] = -min_y + board_offset + radius_y
    
    return drawing_params


def create_hex_styles(custom_hex_styles):
    
    hex_styles = {"1":{"fill":"white", "stroke-width":"1", "stroke":"black"},
                 "2":{"fill":"blue", "stroke-width":"1", "stroke":"black"},
                 "3":{"fill":"green", "stroke-width":"1", "stroke":"black"},
                 "4":{"fill":"yellow", "stroke-width":"1", "stroke":"black"},
                 "5":{"fill":"gray", "stroke-width":"1", "stroke":"black"},
                 "6":{"fill":"black", "stroke-width":"1", "stroke":"black"},
                 "7":{"fill":"red", "stroke-width":"1", "stroke":"black"},
                 "8":{"fill":"purple", "stroke-width":"1", "stroke":"black"},
                 "9":{"fill":"pink", "stroke-width":"1", "stroke":"black"}}
    
    style_strings = {}
    
    if not custom_hex_styles == None:
        for k, custom_hex_style in custom_hex_styles.items():
            if custom_hex_style != None:
                for key, value in custom_hex_style.items():
                    hex_styles[k][key] = value
    
    for hex_type, hex_style in hex_styles.items():
        style_str = ";".join(key+":"+value for key,value in hex_style.items())
        style_strings[hex_type] = style_str
    
    return style_strings


def draw_hex_on_svg(svg_root, x, y, hex_radius, pointy_top=False, style_str=""):

    if pointy_top:
        start_angle = 0
    else:
        start_angle = 30
        
    points = []
    
    for i in range(6):
        angle = start_angle + (360 * i / 6)
        radian = angle * math.pi / 180.
        
        px = x + hex_radius * math.sin(radian)
        py = y + hex_radius * math.cos(radian)
        
        points.append((px, py))
    
    points_str = " ".join([",".join([str(x) for x in coords]) for coords in points])
    
    polygon = etree.SubElement(svg_root, "polygon")
    polygon.set("points", points_str)
    polygon.set("style", style_str)


def create_svg_document(board, drawing_params, hex_radius, hex_offset, x_scale, y_scale, pointy_top=False, background_color="white", custom_hex_styles=None):
    
    svg_root = etree.Element("svg")
    
    width = int(drawing_params["width"])
    height = int(drawing_params["height"])
    x_offset = drawing_params["x_offset"]
    y_offset = drawing_params["y_offset"]
    
    svg_root.set("width", str(width))
    svg_root.set("height", str(height))
    svg_root.set("version", "1.1")
    svg_root.set("xmlns", "http://www.w3.org/2000/svg")
    
    #TODO: put axis as global and create proper method for turning board coordinates into screen coordinates 
    rect = etree.SubElement(svg_root, "rect")
    rect.set("width", str(width))
    rect.set("height", str(height))
    rect.set("fill", background_color)

    if pointy_top:
        x_angle = 0
    else:
        x_angle = 30
    
    y_angle = x_angle + 60
    
    x_axis = (math.cos(x_angle * math.pi / 180.0), math.sin(x_angle * math.pi / 180.0))
    y_axis = (math.cos(y_angle * math.pi / 180.0), math.sin(y_angle * math.pi / 180.0))
    
    scale = hex_radius*math.sqrt(3) + hex_offset
    
    style_strings = create_hex_styles(custom_hex_styles)
    
    for x in range(len(board)):
        for y in range(len(board[0])):
            if board[x][y] != 0:
                coord_x = x_offset + (x_axis[0]*x + y_axis[0]*y)*scale*x_scale
                coord_y = y_offset + (x_axis[1]*x + y_axis[1]*y)*scale*y_scale
                style_str = style_strings[str(board[x][y])]
                draw_hex_on_svg(svg_root, coord_x, coord_y, hex_radius, pointy_top, style_str)
    
    return svg_root 


def create_hex_board_svg(board, hex_radius = 50, hex_offset = 10, board_offset = None, pointy_top=False, background_color = "white", custom_hex_styles = None, x_scale = 1., y_scale = 1.):
    
    if board_offset == None:
        board_offset = hex_radius
    
    #TODO: do not use intermediate coords - calculate drawing params from board
    list_of_coords = get_intermediate_coords(board, pointy_top, x_scale, y_scale)
    
    scaled_coords = scale_coordinates(list_of_coords, hex_radius, hex_offset)
    
    drawing_params = get_drawing_params(scaled_coords, hex_radius, board_offset, pointy_top)
    
    svg_root = create_svg_document(board, drawing_params, hex_radius, hex_offset, x_scale, y_scale, pointy_top, background_color, custom_hex_styles)
    
    return svg_root


if __name__ == "__main__":
    simple_board = generate_triangular_board(5)
    svg_root = create_hex_board_svg(pointy_top=True, board=simple_board, hex_offset=0, custom_hex_styles={"1":{"fill":"white", "stroke":"black", "stroke-width":"2"}})#, background_color="blue")#, custom_hex_styles={"1":{"fill":"green", "stroke":"lime", "stroke-width":"3"}})
    svg_tree = etree.ElementTree(svg_root)
    svg_tree.write("board.svg", pretty_print=True, xml_declaration=True, encoding="utf-8")