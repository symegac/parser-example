from collections.abc import Generator
from typing import Any, Self

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

def pretty_table(table: "Table", colwidth: int = 10) -> str:
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

    header = table.header
    rows = table.rows

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
        return pretty_table(self, self.colwidth)

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

    def select(self, start: int | None = None, stop: int | None = None) -> Generator[Any]:
        """
        Returns the specified range of rows as an iterator

        :param start: Index of first row in range, defaults to None (first row of table)
        :type start: int | None
        :param stop: Index of last row in range, defaults to None (last row of table)
        :type stop: int | None
        """
        if start is None:
            start = 0
        if stop is None:
            stop = len(self.rows)

        for i in range(start, stop):
            yield self.rows[i]

    def range(self, start: int | None = None, stop: int | None = None) -> Self:
        """
        Returns the specified range of rows as a new table with same header

        :param start: Index of first row in range, defaults to None (first row of table)
        :type start: int | None
        :param stop: Index of last row in range, defaults to None (last row of table)
        :type stop: int | None
        """
        return self.__class__(
            header=self.header,
            rows=list(self.select(start, stop)),
            **self.types
        )

    def head(self, rows: int = 10) -> Self:
        """
        Returns the first N rows as a new table with same header

        :param rows: The first N rows
        :type rows: int
        """
        return self.range(stop=rows)

    def tail(self, rows: int = 10) -> Self:
        """
        Returns the last N rows as a new table with same header

        :param rows: The last N rows
        :type rows: int
        """
        return self.range(start=-rows)

    def sort(self, index: str | int = 0, reverse: bool = False) -> Self:
        """
        Returns new table with same header sorted by specified column

        :param index: The column to be sorted by, defaults to `0` (first column)
        :type index: str | int
        :param reverse: Whether the sorting is descending, defaults to False
        :type reverse: bool
        """
        sorted_rows = self.itersort(index=index, reverse=reverse)

        return self.__class__(
            header=self.header,
            rows=sorted_rows,
            **self.types
        )

    def iterhead(self, rows: int = 10) -> Generator[Any]:
        """
        Returns the first N rows of the table as an iterator

        :param rows: The first N rows
        :type rows: int
        """
        return self.select(stop=rows)

    def itertail(self, rows: int = 10) -> Generator[Any]:
        """
        Returns the last N rows of the table as an iterator

        :param rows: The last N rows
        :type rows: int
        """
        return self.select(start=-rows)

    def itersort(self, index: str | int = 0, reverse: bool = False) -> Rows:
        """
        Returns rows sorted by specified column

        :param index: The column to be sorted by, defaults to `0` (first column)
        :type index: str | int
        :param reverse: Whether the sorting is descending, defaults to False
        :type reverse: bool
        """
        if isinstance(index, str):
            if self.header is None:
                raise IndexError("Cannot use string as index. Table has no column names.")
            else:
                index = self.header.index(index)

        sorter = lambda x: x[index]

        return sorted(self.rows, key=sorter, reverse=reverse)
