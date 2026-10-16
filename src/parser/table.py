from typing import Any

from src.parser.types import Header, Rows, TypeCaster
from src.parser.util import get_max_len, truncate

def pretty_header(header: Header, colwidth: int, *, continues: bool = False) -> str:
    """
    Pretty formats a table header for printing

    :param header: The header to print
    :type header: Header
    :param colwidth: The printed width of each column
    :type colwidth: int
    :param continues: Whether the header is followed by rows, defaults to `False`
    :type continues: bool
    """
    top = '-' * ((colwidth + 3) * len(header) - 1)
    colnames = '|'.join(f" {truncate(col, colwidth):<{colwidth}} " for col in header)
    bottom = '|'.join('-' * (colwidth + 2) for _ in header) if continues else top

    output = '\n'.join((top, colnames, bottom))

    return output

def pretty_rows(rows: Rows, colwidth: int) -> str:
    """
    Pretty formats table rows for printing

    :param rows: The rows to print
    :type rows: Rows
    :param colwidth: The printed width of each column
    :type colwidth: int
    """
    row_strings = []

    for row in rows:
        fields = []
        for field in row:
            align = '>' if isinstance(field, int | float) else '<'
            fields.append(f" {truncate(field, colwidth):{align}{colwidth}} ")
        row_strings.append('|'.join(fields))

    output = '\n'.join(row_strings)

    return output

def pretty_table(header: Header | None, rows: Rows, colwidth: int = 10) -> str:
    """
    Pretty formats a table for printing
    
    :param header: The header to print
    :type header: Header | None
    :param rows: The rows to print
    :type rows: Rows
    :param colwidth: The printed width of each column, defaults to `10`
    :type colwidth: int
    """
    parts = []

    if header is not None:
        parts.append(pretty_header(header, colwidth, continues=True))
    parts.append(pretty_rows(rows, colwidth))

    return '\n'.join(parts)

class Table:
    """Table for viewing and selecting data, with optional type conversion"""
    def __init__(
        self,
        header: Header | None = None,
        rows: Rows | None = None,
        **coltypes: TypeCaster
    ) -> None:
        """
        Table for viewing and selecting data, with optional type conversion

        :param header: The header of the table, defaults to `None`
        :type header: Header | None
        :param rows: The rows of the table, defaults to `None`
        :type rows: Rows | None
        :param coltypes: Type or callable to cast data in a column into new type
        :type coltypes: TypeCaster
        """
        self.header: Header | None = list(header) if header is not None else header
        self.rows: Rows = self.load_rows(header=header, rows=rows, **coltypes) or []
        self.types = coltypes

    @property
    def columns(self) -> list[Any]:
        """Column view of table data"""
        return list(zip(*self.rows))

    @property
    def colwidth(self) -> int:
        """Gets column width from header"""
        return get_max_len(self.header) if self.header is not None else 10

    def __str__(self) -> str:
        return pretty_table(self.header, self.rows, self.colwidth)

    def load_rows(
        self,
        header: Header | None = None,
        rows: Rows | None = None,
        **coltypes: TypeCaster
    ) -> list[list[Any]]:
        if rows is None:
            return []
        if header is None:
            header = []

        types: list[TypeCaster | None] = [coltypes.pop(colname, None) for colname in header]
        loaded_rows = []

        for row in rows:
            loaded_row = []

            for colindex, field in enumerate(row):
                tp = types[colindex]

                if tp is not None:
                    try:
                        field = tp(field)
                    except:
                        pass

                loaded_row.append(field)

            loaded_rows.append(loaded_row)

        return loaded_rows
