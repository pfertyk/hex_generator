import os
from unittest import TestCase
from testfixtures.comparison import compare
from testfixtures.tempdirectory import TempDirectory
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

    def test_generate_board_triangle_lower(self):
        board = hg.generate_triangular_board(5, upper=False)
        expected_board = [
            [0, 0, 0, 0, 1],
            [0, 0, 0, 1, 1],
            [0, 0, 1, 1, 1],
            [0, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
        ]
        self.assertEqual(board, expected_board)

    def test_generate_board_hexagon(self):
        board = hg.generate_hexagonal_board(3)
        expected_board = [
            [0, 0, 0, 1, 1, 1, 1],
            [0, 0, 1, 1, 1, 1, 1],
            [0, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 0],
            [1, 1, 1, 1, 1, 0, 0],
            [1, 1, 1, 1, 0, 0, 0],
        ]
        self.assertEqual(board, expected_board)


class BoardFileTests(TestCase):
    def test_write_board_to_text_file(self):
        board = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [9, 9, 9],
        ]
        with TempDirectory() as d:
            hg.write_board_to_text_file(board, os.path.join(d.path, 'test.txt'))
            compare(d.read('test.txt', 'utf-8'), '0 3 6 9\n1 4 7 9\n2 5 8 9\n')

    def test_write_board_to_text_file_padding(self):
        board = [
            [0, 1, 2],
            [3, 4],
            [6, 7, 8],
            [9],
        ]
        with TempDirectory() as d:
            hg.write_board_to_text_file(board, os.path.join(d.path, 'test.txt'))
            compare(d.read('test.txt', 'utf-8'), '0 3 6 9\n1 4 7 0\n2 0 8 0\n')

    def test_read_board_from_text_file(self):
        expected_board = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [9, 9, 9],
        ]
        with TempDirectory() as d:
            d.write('test.txt', '0 3 6 9\n1 4 7 9\n2 5 8 9\n', 'utf-8')
            board = hg.read_board_from_text_file(os.path.join(d.path, 'test.txt'))
            self.assertEqual(board, expected_board)

    def test_read_board_from_text_file_padding(self):
        expected_board = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 0, 8],
            [9, 0, 0],
        ]
        with TempDirectory() as d:
            d.write('test.txt', '0 3 6 9\n1 4\n2 5 8\n', 'utf-8')
            board = hg.read_board_from_text_file(os.path.join(d.path, 'test.txt'))
            self.assertEqual(board, expected_board)
