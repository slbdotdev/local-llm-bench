"""Table presenters with configurable columns."""

from .. import core


def table_row(row, columns, tone="plain"):
    result = []
    for column in columns:
        value = row[column]
        result.append(core.make_badge(value, tone=tone))
    return result


def table(rows, columns=("label",), tone="plain"):
    return [table_row(row, columns, tone=tone) for row in rows]


def text(rows, columns=("label",), tone="plain"):
    return "\n".join(" | ".join(value) for value in table(rows, columns, tone))


def widths(rows, columns=("label",)):
    return {column: max((len(str(row[column])) for row in rows), default=0)
            for column in columns}


def sort_rows(rows, column="label", tone="plain"):
    return table(sorted(rows, key=lambda row: row[column]), (column,), tone=tone)
