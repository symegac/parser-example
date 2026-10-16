import os
import unittest

from parser.types import delim, DelimiterError, EOL

class TestTypes(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.valid_delimiters = [',', '\t', ';', '|', 2, delim(',')]
        cls.invalid_delimiters = ["Invalid", ", ", None, 1.23, 23, {1}, '"', '\"']

    def test_delim_invalid(self) -> None:
        for obj in self.invalid_delimiters:
            with self.assertRaises(DelimiterError):
                delim(obj)

    def test_delim_valid(self) -> None:
        for obj in self.valid_delimiters:
            converted = delim(obj)
            self.assertIsInstance(converted, delim)
            self.assertIsInstance(converted, str)

            self.assertEqual(converted, converted[0])
            self.assertEqual(converted, str(obj))

    def test_delim_repr(self) -> None:
        for obj in self.valid_delimiters:
            converted = delim(obj)
            self.assertEqual(repr(converted), f"delim('{converted}')")

            if isinstance(obj, delim):
                self.assertEqual(repr(converted), repr(obj))
            else:
                self.assertNotEqual(repr(converted), repr(obj))

    def test_eol_from_system(self) -> None:
        windows = os.name == "nt"
        eol_sequence = EOL.from_system()

        self.assertIs(eol_sequence, EOL.CRLF if windows else EOL.LF)
