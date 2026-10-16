import unittest
import sys

from parser.csv_parser import ParserConfig
from parser.types import delim, EOL

class TestParserConfig(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verbose = '-v' in sys.argv or "--verbose" in sys.argv

        cls.strict_values = [
            (delim(','), EOL.LF),
            (delim('\t'), EOL.CR),
            (delim(';'), EOL.CRLF),
            (delim('|'), EOL.LFCR)
        ]
        cls.castable_values = [
            (',', '\n'),
            ('\t', '\r'),
            (';', "\r\n"),
            ('|', "\n\r"),
        ]
        cls.non_castable_delimiters = ['', ",,"]
        cls.non_castable_newlines = ["\n\n", "\r\r", '\t', "newline"]
        cls.invalid_values = [2, 3.14, 2/4, {0, 1, 2}, {"invalid": "value"}, ["not", "valid"]]

    def test_config_frozen(self) -> None:
        config = ParserConfig()

        with self.assertRaises(AttributeError):
            config.delimiter = 'a' # type: ignore

    def test_config_strict_values(self) -> None:
        for delimiter, newline in self.strict_values:
            config = ParserConfig(delimiter=delimiter, newline=newline, strict=True)

            # equal in value AND identity
            self.assertIs(config.delimiter, delimiter)
            self.assertIs(config.newline, newline)

    def test_config_strict_castable_values(self) -> None:
        for delimiter, newline in self.castable_values:
            try:
                config = ParserConfig(delimiter=delimiter, newline=newline, strict=True)
            except:
                self.fail("Casting of castable values should not raise an exception")

            # equal in value, not in identity
            self.assertEqual(config.delimiter, delimiter)
            self.assertEqual(config.newline, newline)

    def test_config_strict_non_castable_values(self) -> None:
        for delimiter in self.non_castable_delimiters:
            with self.assertRaises(ValueError):
                ParserConfig(delimiter=delimiter, newline=EOL.LF, strict=True)

        for newline in self.non_castable_newlines:
            with self.assertRaises(ValueError):
                ParserConfig(delimiter=delim(','), newline=newline, strict=True)

    def test_config_lax_any_value(self) -> None:
        value_pairs = [
            self.strict_values,
            self.castable_values,
            zip(self.non_castable_delimiters, self.non_castable_newlines)
        ]

        for value_pair in value_pairs:
            for delimiter, newline in value_pair:
                config = ParserConfig(delimiter=delimiter, newline=newline, strict=False)

                self.assertIs(config.delimiter, delimiter)
                self.assertIs(config.newline, newline)

    def test_config_invalid_values(self) -> None:
        for invalid_value in self.invalid_values:
            for strict in (True, False):
                with self.assertRaises(TypeError):
                    ParserConfig(delimiter=invalid_value, newline=EOL.LF, strict=strict)
                with self.assertRaises(TypeError):
                    ParserConfig(delimiter=delim(','), newline=invalid_value, strict=strict)
                with self.assertRaises(TypeError):
                    ParserConfig(delimiter=invalid_value, newline=invalid_value, strict=strict)
