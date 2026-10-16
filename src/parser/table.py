from typing import Any

from src.parser.types import Header, Rows, TypeCaster

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

    def __str__(self) -> str:
        output = ''

        if self.header is not None:
            header = "\t|\t".join(self.header)
            output += header + '\n'

        rows = '\n'.join("\t|\t".join(row) for row in self.rows)
        output += rows

        return output

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
