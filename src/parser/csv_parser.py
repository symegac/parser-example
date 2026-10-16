from dataclasses import dataclass, field, InitVar

from src.parser.types import delim, DelimiterError, EOL

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
