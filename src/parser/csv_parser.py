from dataclasses import dataclass, field, InitVar
from typing import Protocol

from src.parser.types import delim, DelimiterError, EOL, Line

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
