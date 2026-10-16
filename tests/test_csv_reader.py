import json
import unittest

from pathlib import Path

from parser.csv_parser import CSVReader, StandardCSVParser, ParserConfig
from parser.types import CSVSyntaxError, delim, EOL
from parser.util import read_file

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

    def test_reader_to_dict(self) -> None:
        for test_file in self.valid_files:
            if not test_file["header"]:
                continue

            path = self.DATA_PATH / test_file["path"]
            reader = CSVReader(path, parser=self.parser)

            export = reader.to_dict()

            self.assertEqual(len(export["rows"]), test_file["rows"])
            self.assertEqual(export["header"], test_file["header"])
            self.assertEqual(list(export["rows"][0].keys()), test_file["header"])
            self.assertEqual(list(export["rows"][0].values()), test_file["first_row"])

    def test_reader_to_json(self) -> None:
        for test_file in self.valid_files:
            if not test_file["header"]:
                continue

            path = self.DATA_PATH / test_file["path"]
            reader = CSVReader(path, parser=self.parser)

            export = reader.to_dict()
            json_export = reader.to_json()

            self.assertEqual(export, json.loads(json_export))

    def test_reader_reload_changed_parser_config(self) -> None:
        test_file = self.invalid_files[0]
        path = self.DATA_PATH / test_file["path"]
        parser = StandardCSVParser(config=self.parser_config)

        # standard config
        reader = CSVReader(path, parser=parser)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=path,
            header=test_file["header"] or None,
            rows=test_file["rows"],
            first_row=test_file["first_row"]
        )

        # changed config
        reader.parser.delimiter = delim('a')
        reader.reload(full=False)

        self.assertEqual(reader.header, ['n', 'me,em', 'il,dep', 'rtment,role,s', 'l', 'ry,st', 'rt_d', 'te,office'])
        self.assertEqual(reader.rows[0], ['M', 'rcus Chen,m', 'rcus.chen@ex', 'mple.com,Engineering,Senior Softw', 're Engineer,155000,2019-03-15,S', 'n Fr', 'ncisco', ''])

    def test_reader_reload_changed_file_contents(self) -> None:
        test_file = self.valid_files[0]
        path = self.DATA_PATH / test_file["path"].replace("employees.csv", "rw.csv")
        parser = StandardCSVParser(config=self.parser_config)

        reader = CSVReader(path, parser=parser)

        appended = 'a'
        original_contents = read_file(path)
        new_contents = original_contents + appended

        with open(path, 'w', encoding="utf-8") as file:
            file.write(new_contents)

        reader.reload(full=True)

        original_field = test_file["first_row"][-1]
        new_field = reader.rows[0][-1]
        self.assertNotEqual(new_field, original_field)
        self.assertEqual(new_field, original_field + appended)

        # remember to return file to original state
        with open(path, 'w', encoding="utf-8") as file:
            file.write(original_contents)

    def test_reader_reload_new_path(self) -> None:
        test_file = self.valid_files[0]
        path = self.DATA_PATH / test_file["path"]
        parser = StandardCSVParser(config=self.parser_config)

        reader = CSVReader(path, parser=parser)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=path,
            header=test_file["header"] or None,
            rows=test_file["rows"],
            first_row=test_file["first_row"]
        )

        test_file = self.valid_files[1]
        new_path = self.DATA_PATH / test_file["path"]
        reader.reload(new_path=new_path)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=new_path,
            header=test_file["header"] or None,
            rows=test_file["rows"],
            first_row=test_file["first_row"]
        )

    def test_reader_reload_new_invalid_path(self) -> None:
        test_file = self.valid_files[0]
        path = self.DATA_PATH / test_file["path"]
        parser = StandardCSVParser(config=self.parser_config)

        reader = CSVReader(path, parser=parser)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=path,
            header=test_file["header"] or None,
            rows=test_file["rows"],
            first_row=test_file["first_row"]
        )

        new_path = self.DATA_PATH / "invalid" / "path"
        reader.reload(new_path=new_path)

        # new invalid path has no effect
        self.assertEqual(reader.path, path)
        self.assertCorrectlyReadsCSV(
            reader=reader,
            path=path,
            header=test_file["header"] or None,
            rows=test_file["rows"],
            first_row=test_file["first_row"]
        )
