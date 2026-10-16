import json
import unittest
import sys

from pathlib import Path

from parser.csv_parser import StandardCSVParser
from parser.util import get_max_len

class TestCSVParser(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verbose = '-v' in sys.argv or "--verbose" in sys.argv
        cls.parser = StandardCSVParser()

        with open(Path(__file__).parent / "data" / "test_csv_parser.json", 'r', encoding="utf-8") as data:
            test_data = json.load(data)

        cls.whitespace_io: dict[str, list[str]] = test_data["whitespace_tests_io_map"]
        cls.delimiter_input: list[str] = test_data["delimiter_tests"]["input_strings"]
        cls.delimiter_output: dict[str, list[list[str]]] = test_data["delimiter_tests"]["delimited_output_map"]
        cls.quote_io: dict[str, list[str]] = test_data["quote_tests_io_map"]

    def setUp(self) -> None:
        if self.verbose:
            print()

    def _print_line_parse_io(self, i: str, o: list[str], max_input_len: int, delimiter: str) -> None:
        print(
            f"Input: {i!r} ".ljust(max_input_len + 15, '-') + '>',
            f"Output (w/ {delimiter!r:>4}): {o}"
        )

    def _customize_input_strings(self, input_strings: list[str], /, new_delimiter: str) -> list[str]:
        for i, string in enumerate(input_strings):
            input_strings[i] = string.replace(new_delimiter, '\"').replace(',', new_delimiter)

        return input_strings

    def assertDelimiterSplitsCorrectly(self, delimiter: str) -> None:
        input_strings = self.delimiter_input.copy()

        if delimiter not in self.delimiter_output:
            input_strings = self._customize_input_strings(input_strings, new_delimiter=delimiter)

        delimited_outputs = self.delimiter_output.get(delimiter, self.delimiter_output[','])

        if len(delimited_outputs) != len(input_strings):
            self.fail(f"Expected output of {delimiter!r} not defined for all input strings")

        max_input_len = get_max_len(input_strings)

        for input_string, expected_output in zip(input_strings, delimited_outputs):
            parsed_line = self.parser._parse_line(input_string, delimiter=delimiter)

            self.assertEqual(parsed_line, expected_output)
            self.assertEqual(input_string.count(delimiter) + 1, len(parsed_line))

            if self.verbose:
                self._print_line_parse_io(input_string, expected_output, max_input_len, delimiter)

    def test_parse_line_whitespace(self) -> None:
        for input_string, expected_output in self.whitespace_io.items():
            self.assertEqual(self.parser._parse_line(input_string), expected_output)

    def test_parse_line_valid_delimiter(self) -> None:
        for delimiter in self.delimiter_output:
            self.assertDelimiterSplitsCorrectly(delimiter)

    def test_parse_line_undefined_delimiter(self) -> None:
        self.assertDelimiterSplitsCorrectly('§')

    def test_parse_line_invalid_delimiter(self) -> None:
        with self.assertRaises(ValueError, msg="'\"' as delimiter successfully blocked") as exc:
            self.parser._parse_line('', delimiter='"')

        if self.verbose:
            print('\n', exc.msg, sep='')

    def test_quoted_string(self) -> None:
        max_input_len = get_max_len(self.quote_io)

        for input_string, expected_output in self.quote_io.items():
            self.assertEqual(self.parser._parse_line(input_string, delimiter=',', retain_whitespace=False), expected_output)

            if self.verbose:
                self._print_line_parse_io(input_string, expected_output, max_input_len=max_input_len, delimiter=',')
