from unittest import TestCase
from hex_generator import generate_board


class BoardGenerationTests(TestCase):
    def test_generate_board_rhombus(self):
        board = generate_board(5, 3, 'rhombus')
        expected_board = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ]
        expected_board = [list(x) for x in zip(*expected_board)]
        self.assertEqual(board, expected_board)

    def test_generate_board_rectangle(self):
        board = generate_board(5, 3, 'rectangular')
        expected_board = [
            [0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 0, 0, 0],
        ]
        expected_board = [list(x) for x in zip(*expected_board)]
        self.assertEqual(board, expected_board)

    def test_generate_board_triangle(self):
        board = generate_board(5, 3, 'triangular')
        expected_board = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
            [1, 1, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ]
        expected_board = [list(x) for x in zip(*expected_board)]
        self.assertEqual(board, expected_board)

    def test_generate_board_hex(self):
        board = generate_board(5, 5, 'hexagonal')
        expected_board = [
            [0, 0, 1, 1, 1],
            [0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 0],
            [1, 1, 1, 0, 0],
        ]
        expected_board = [list(x) for x in zip(*expected_board)]
        self.assertEqual(board, expected_board)
