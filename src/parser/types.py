import os

from enum import StrEnum
from typing import Any, Self

type Line = list[str]
type Header = Line
type Rows = list[Line]

class CSVError(Exception):
    ...

class DelimiterError(ValueError, CSVError):
    ...

class delim(str):
    """Single-character delimiter string"""
    def __new__(cls, char: str | Any) -> Self:
        char = str(char)

        if len(char) != 1:
            raise DelimiterError("A delimiter character must be exactly one character long")
        if char == '"':
            raise DelimiterError("A double quotation mark cannot be used as a delimiter character")

        return super().__new__(cls, char)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}('{self}')"

class EOL(StrEnum):
    """Character or character sequence signifying End Of Line"""

    CR = '\r'
    CRLF = "\r\n"
    LF = '\n'
    LFCR = "\n\r"

    POSIX = LF
    """POSIX-conformant or Unix-like systems (e.g, Linux, macOS, BSD, etc.)"""
    NT = CRLF
    """Windows"""

    @classmethod
    def from_system(cls) -> Self:
        return cls[os.name.upper()]
