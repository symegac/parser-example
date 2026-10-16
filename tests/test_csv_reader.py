import json
import unittest

from pathlib import Path

from src.parser.csv_parser import CSVReader, StandardCSVParser, ParserConfig
from src.parser.types import CSVSyntaxError, delim, EOL
from src.parser.util import read_file

class TestCSVReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.DATA_PATH = Path(__file__).parent / "data"

        with open(Path(__file__).parent / "data" / "test_csv_reader.json", 'r', encoding="utf-8") as data:
            test_data = json.load(data)

        cls.valid_files: list[dict] = test_data["valid_files"]
        cls.invalid_files: list[dict] = test_data["invalid_files"]

        cls.parser_config = ParserConfig(newline=EOL.POSIX)
        cls.parser = StandardCSVParser(config=cls.parser_config)

    def assertCorrectlyReadsCSV(
        self,
        reader: CSVReader,
        path: Path,
        header: list[str] | None,
        rows: int,
        first_row: list[str] | None
    ) -> None:
        # correctly stores raw data
        self.assertEqual(reader.raw_data, read_file(path))

        if header is None:
            self.assertIsNone(reader.header)

        # correctly reads header
        self.assertEqual(reader.header, header)

        # correctly splits lines (TODO: test for empty line retention)
        self.assertEqual(len(reader.rows), rows)

        if reader.header is not None and rows > 0:
            # rows contain all columns
            self.assertEqual(len(reader.header), len(reader.rows[0]))

        if rows > 0 and first_row is None:
            raise ValueError("No first row given for non-empty reader")

        # correctly reads lines
        self.assertEqual(reader.rows[0], first_row)

    def test_reader(self) -> None:
        for test_file in self.valid_files:
            path = self.DATA_PATH / test_file["path"]
            reader = CSVReader(path, parser=self.parser, contains_header=bool(test_file["header"]))
            self.assertCorrectlyReadsCSV(
                reader=reader,
                path=path,
                header=test_file["header"] or None,
                rows=test_file["rows"],
                first_row=test_file["first_row"]
            )

    def test_reader_headerless(self) -> None:
        for test_file in self.valid_files:
            path = self.DATA_PATH / test_file["path"]
            reader = CSVReader(path, parser=self.parser, contains_header=False)
            self.assertCorrectlyReadsCSV(
                reader=reader,
                path=path,
                header=None,
                rows=test_file["rows"] + 1,
                first_row=test_file["header"]
            )

    def test_reader_throws_incongruent_field_length(self) -> None:
        test_file = self.valid_files[0]
        path = self.DATA_PATH / test_file["path"]
        config = ParserConfig(delimiter='a', newline=EOL.POSIX)
        parser = StandardCSVParser(config=config)

        with self.assertRaises(CSVSyntaxError):
            CSVReader(path, parser=parser)

    def test_reader_skip_invalid_lines(self) -> None:
        test_file = self.valid_files[0]
        path = self.DATA_PATH / test_file["path"]
        config = ParserConfig(delimiter='a', newline=EOL.POSIX)
        parser = StandardCSVParser(config=config)

        try:
            CSVReader(path, parser=parser, skip_invalid_lines=True)
        except CSVSyntaxError:
            self.fail("Reader didn't skip line with invalid syntax")

    def test_reader_retain_empty_lines(self) -> None:
        test_file = self.invalid_files[0]
        path = self.DATA_PATH / test_file["path"]

        reader = CSVReader(path, parser=self.parser, retain_empty_lines=True)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=path,
            header=test_file["header"],
            rows=test_file["rows"] + 1,
            first_row=test_file["first_row"]
        )
