import unittest
import sys

from decimal import Decimal
from pathlib import Path

from src.parser.util import get_max_len, read_file, truncate

class TestUtil(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verbose = '-v' in sys.argv or "--verbose" in sys.argv

        cls.DATA_PATH = Path(__file__).parent / "data"

        cat = {"name": "Mittens", "age": 4, "breed": "Ragdoll", "colour": "Tabby"}

        cls.max_lengths = {
            0: [''],
            1: ('', '', '', ' ', ''),
            2: [24 // 2], # -> 12
            3: [.0, 0., 1., .1, 1/2], # -> 0.0, 1.0, 0.1, 0.5
            4: [None, 24 / 2], # -> 12.0
            6: cat, # -> "colour"
            7: cat.values(), # -> "Mittens", "Ragdoll"
            8: {"22", "333", "55555", "88888888", "1313", "21"},
            11: [333, 4444, 666666, 999999999, 11111111111],
            12: ["aaaaaa", "aaaaaaaaaaa", "AAAAAAA", "AAAAAAAAAAAA", "aaAaAAaA"],
            14: [3.141592653589, 9.876543, .0], # -> "3.141592653589"
            18: ((1), (1, 2), (1, 2, 3), (1, 2, 3, 4, 5, 6)), # -> "(1, 2, 3, 4, 5, 6)"
        }

        cls.truncatables = [
            '',
            "testtesttest",
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            2345,
            0.00000000,
            3.141592653589,
            Decimal("3.141592653589"),
        ]

    def test_read_file(self) -> None:
        files = self.DATA_PATH.iterdir()

        for file in files:
            if file.is_file():
                file_data = read_file(file)

                self.assertIsInstance(file_data, str)
                self.assertTrue(file_data)
                self.assertIn('\n', file_data)

    def test_read_file_invalid_path(self) -> None:
        with self.assertRaises(FileNotFoundError):
            read_file(self.DATA_PATH / "invalid_path")
            read_file(self.DATA_PATH / '')
            read_file(self.DATA_PATH)

        with self.assertRaises(TypeError):
            read_file(2) # type: ignore

    def test_get_max_len(self) -> None:
        for max_len, iterable in self.max_lengths.items():
            self.assertEqual(get_max_len(iterable), max_len)

    def test_get_max_len_empty(self) -> None:
        for collection in (list, tuple, set, dict):
            self.assertEqual(get_max_len(collection()), 0)

    def test_truncate(self) -> None:
        input_objects = self.truncatables

        if self.verbose:
            print()

        for length in range(20):
            for input_object in input_objects:
                if length <= 3:
                    self.assertEqual(truncate(input_object, max_len=length), "...")
                else:
                    self.assertLessEqual(len(truncate(input_object, max_len=length)), length)

                if self.verbose:
                    print(f"{input_object!r} > {truncate(input_object, max_len=length)!r} (len: {length})")
