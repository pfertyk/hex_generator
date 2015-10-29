from unittest import TestCase
import hex_generator as hg


class BoardGenerationTests(TestCase):
    def test_generate_board_rhombus(self):
        board = hg.generate_rhomboidal_board(5, 3)
        expected_board = [
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_rectangle(self):
        board = hg.generate_rectangular_board(5, 3)
        expected_board = [
            [0, 0, 1, 1, 1],
            [0, 0, 1, 1, 1],
            [0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_rectangle_pointy_top(self):
        board = hg.generate_rectangular_board(5, 3, pointy_top=True)
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
        board = hg.generate_triangular_board(5)
        expected_board = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_hexagon(self):
        board = hg.generate_hexagonal_board(5, 3)
        expected_board = [
            [0, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 1],
            [1, 1, 0],
        ]
        self.assertEqual(board, expected_board)
