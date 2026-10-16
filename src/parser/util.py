from pathlib import Path

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
