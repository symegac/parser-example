import re

from dataclasses import dataclass, field, InitVar
from pathlib import Path
from typing import Protocol

from src.parser.types import delim, DelimiterError, EOL, Line, Rows
from src.parser.util import read_file, WHITESPACE

@dataclass(frozen=True)
class ParserConfig:
    """
    Configuration parameters for a CSV parser

    :param delimiter: The delimiter splitting line entries, defaults to `delim(',')`
    :type delimiter: delim | str
    :param newline: The delimiter indicating EOL and splitting lines, defaults to `EOL.LF` (POSIX) or `EOL.CRLF` (Windows)
    :type newline: EOL | str
    :param retain_whitespace: Controls retention of whitespace between line items, defaults to `False`
    :type retain_whitespace: bool
    :param strict: Restricts delimiter to a single character, and newline to predefined sequences of CR and LF, and tries to cast other types to those, defaults to `True`
    :type strict: bool
    """
    delimiter: delim | str = delim(',')
    newline: EOL | str = EOL.from_system()
    retain_whitespace: bool = False
    strict: InitVar[bool] = field(kw_only=True, default=True)

    def __post_init__(self, strict: bool = True) -> None:
        if not isinstance(self.delimiter, str):
            raise TypeError("Field delimiter must be a str or subclass thereof")
        if not isinstance(self.newline, str):
            raise TypeError("Newline delimiter must be a str or subclass thereof")

        if not strict:
            return
        
        if not isinstance(self.delimiter, delim):
            try:
                super().__setattr__("delimiter", delim(self.delimiter))
            except DelimiterError as err:
                raise DelimiterError(f"{self.delimiter!r} is not a valid field delimiter in strict mode: {err.args[0]}")

        if not isinstance(self.newline, EOL):
            try:
                super().__setattr__("newline", EOL(self.newline))
            except ValueError as err:
                raise DelimiterError(f"{err.args[0]} delimiter in strict mode: Only control characters LF, CR or a combination thereof can be used as newline character")

STANDARD_PARSER_CONFIG = ParserConfig()

# TODO: configurable quote character
class CSVParser(Protocol):
    """Parses CSV strings"""
    delimiter: delim | str
    newline: EOL | str
    retain_whitespace: bool

    def __init__(self, config: ParserConfig = STANDARD_PARSER_CONFIG) -> None:
        """
        :param config: Optional initial configuration of parser, defaults to `STANDARD_PARSER_CONFIG`
        :type config: ParserConfig
        """
        self.configure(config)

    def configure(self, config: ParserConfig | None = None) -> None:
        config = config or STANDARD_PARSER_CONFIG

        self.delimiter = config.delimiter
        self.newline = config.newline
        self.retain_whitespace = config.retain_whitespace

    def split_lines(self, string: str) -> list[str]:
        """
        Splits a CSV-formatted string into lines

        :param string: The string to be split
        :type string: str
        :return lines: list[str]
        """
        ...

    def parse_line(self, string: str) -> Line:
        """
        Parses line items in a CSV-formatted string
        
        :param string: The string to be split
        :type string: str
        :return line: Line
        """
        ...

class StandardCSVParser(CSVParser):
    def split_lines(self, string: str) -> list[str]:
        return self._split_lines(string, newline=self.newline, retain_whitespace=self.retain_whitespace)

    def parse_line(self, string: str) -> Line:
        return self._parse_line(string, delimiter=self.delimiter, retain_whitespace=self.retain_whitespace)

    @staticmethod
    def _split_lines(string: str, /, newline: EOL | str, retain_whitespace: bool) -> list[str]:
        """Actual line splitter implementation in static method to enable testing without initialization and states"""
        # naive implementation, doesn't check for newlines in quoted strings
        return [line for line in string.split(newline) if not (retain_whitespace and not line)]

    @staticmethod
    def _parse_line(string: str, /, delimiter: str = ',', retain_whitespace: bool = False) -> Line:
        """Actual line parser implementation in static method to enable testing without initialization and states"""
        if delimiter == '"':
            raise DelimiterError("A double quotation mark cannot be used as delimiter")

        fields = []

        in_quoted_string = False
        char_buffer = ''

        for i, char in enumerate(string):
            if not retain_whitespace:
                empty_whitespace = char in WHITESPACE and not in_quoted_string and not char_buffer

                if empty_whitespace:
                    continue

                if char == '"':
                    # peeking ahead with regex etc. (cheating?)
                    start_quote_transition = not char_buffer and re.search(fr'"\s*{delimiter}', string[i + 1:]) # actual quote following?
                    end_quote_transition = in_quoted_string and all(c in WHITESPACE for c in string[i + 1:string.find(delimiter, i)]) # more text left?

                    if start_quote_transition or end_quote_transition:
                        in_quoted_string = not in_quoted_string
                    else:
                        char_buffer += '\"'

                    continue

            if char == delimiter:
                if not in_quoted_string:
                    fields.append(char_buffer if retain_whitespace else char_buffer.strip())
                    char_buffer = ''

                    continue

            char_buffer += char
        else:
            fields.append(char_buffer if retain_whitespace else char_buffer.strip())

        return fields

class CSVReader:
    """Reads a CSV file and parses it"""
    def __init__(
        self,
        path: Path | str,
        /,
        parser: CSVParser = StandardCSVParser(),
        contains_header: bool = True,
        *,
        auto: bool = True,
        encoding: str = "utf-8"
    ) -> None:
        """
        Reads a CSV file and parses it

        :param path: The path of the CSV file
        :type path: Path | str
        :param parser: The parser used to parse a CSV string, defaults to `StandardCSVParser()`
        :type parser: CSVParser
        :param contains_header: Whether the CSV string includes a header, defaults to `True`
        :type contains_header: bool
        :param auto: Automatically read and parse file on initialization, defaults to `True`
        :type auto: bool
        :param encoding: The encoding of the CSV file, defaults to `"utf-8"`
        :type encoding: str
        """
        self.path = path
        self.parser = parser
        self.contains_header = contains_header
        self.encoding = encoding

        self.clear()

        if auto:
            self.read()
            self.parse()

    def read(self) -> None:
        self._raw = read_file(path=self.path, encoding=self.encoding)

    def parse(self) -> None:
        lines = self.parser.split_lines(self._raw)

        if self.contains_header:
            header, *lines = lines
            self._header = self.parser.parse_line(header)

        self._rows = []

        for line in lines:
            row = self.parser.parse_line(line)

            self._rows.append(row)

    def clear(self) -> None:
        """Clears read data"""
        self._raw = ''
        self._header = None
        self._rows = []

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: Path | str) -> None:
        self._path = Path(path)

    @property
    def header(self) -> Line | None:
        return self._header

    @property
    def rows(self) -> Rows:
        return self._rows

    @property
    def raw_data(self) -> str:
        return self._raw
