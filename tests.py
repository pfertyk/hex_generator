from unittest import TestCase
from hex_generator import generate_rectangular_board, generate_hexagonal_board, generate_triangular_board, generate_rhomboidal_board


class BoardGenerationTests(TestCase):
    def test_generate_board_rhombus(self):
        board = generate_rhomboidal_board(5, 3)
        expected_board = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_rectangle(self):
        board = generate_rectangular_board(5, 3)
        expected_board = [
            [0, 0, 1, 1, 1],
            [0, 0, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_rectangle_pointy_top(self):
        board = generate_rectangular_board(5, 3, pointy_top=True)
        expected_board = [
            [0, 0, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 0],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_triangle(self):
        board = generate_triangular_board(5, 3)
        expected_board = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_hexagon(self):
        board = generate_hexagonal_board(5, 3)
        expected_board = [
            [0, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 0],
        ]
        self.assertEqual(board, expected_board)
