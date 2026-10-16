import re

from collections.abc import Iterable
from pathlib import Path
from typing import Any

SINGLE_QUOTE_STRING_PATTERN = re.compile(r"'(.+?)'", re.IGNORECASE) # non-greedy
DOUBLE_QUOTE_REPL = r'"\1"'

# https://en.wikipedia.org/wiki/Whitespace_character#Unicode
WHITESPACE = (
    '\t', '\n', '\v', '\f', '\r', ' ',
    '\u0085', '\u00a0', '\u1680',
    '\u2000', '\u2001', '\u2002', '\u2003', '\u2004',
    '\u2005', '\u2006', '\u2007', '\u2008', '\u2009',
    '\u200a',
    '\u2028', '\u2029', '\u202f',
    '\u205f', '\u3000',
)

def read_file(path: Path, encoding: str = "utf-8") -> str:
    """
    Opens file, decodes binary buffer, and returns resulting text string
    
    :param path: The file path
    :type path: Path
    :param encoding: The encoding of the file, defaults to `"utf-8"`
    :type encoding: str
    :return str: The read file
    :raise TypeError: Path not convertible
    :raise FileNotFoundError: Invalid path
    :raise OSError: Other IO errors
    """
    if not isinstance(path, Path | str):
        raise TypeError(f"Path {str(path)!r} invalid, must be a Path or str")

    try:
        with open(path, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(path)
    except OSError:
        raise

def get_max_len(items: Iterable[Any]) -> int:
    """
    Gets the maximum length of the stringified forms of items in a given collection

    :param items: The collection of items
    :type items: Iterable[Any]
    :return int: The maximum string length among input items
    """
    if not items:
        return 0

    lengths = (len(str(item)) for item in items)

    return max(lengths)

def truncate(obj: Any, max_len: int = 10) -> str:
    """
    Truncates string representation of an object to a set maximum length, inserting an ellipsis as indication.
    Correctly rounds decimal numbers (only of type `float`, not `Decimal`) as well.
    
    :param obj: The object to truncate
    :type obj: Any
    :param max_len: The maximum allowed string length, defaults to `10`
    :type max_len: int
    """
    if max_len <= 3:
        return "..."

    original_data_length = len(str(obj))
    max_data_length = max_len - 3

    if isinstance(obj, float):
        integer_length = len(str(obj).split('.')[0])
        if max_len <= 3 + integer_length:
            obj = f"{round(obj)}"
        else:
            obj = f"{obj:.{min(max_data_length - integer_length - 1, original_data_length - integer_length - 1)}f}"

    obj = str(obj)

    truncated_data_length = len(obj)

    if truncated_data_length <= max_len and not (truncated_data_length < original_data_length):
        return obj

    return obj[:max_data_length] + "..."
