from __future__ import annotations
from typing import List


class _Element:
    def __init__(self):
        self.body: str = ''

# only for type hinting


class Document:
    """
    Interface for docx.Document because type hinting is not working

    Not all the fiels are present in this interface
    """

    def __init__(self):
        self.tables: List[Table] = []
        self._element: _Element = None

# interfaces
class ParagraphStyle:
    def __init__(self):
        pass

class Run:
    def __init__(self):
        self.text: str = ''


class Paragraph:
    def __init__(self):
        self.runs: List[Run] = None
        self.text = ''
        self.style:ParagraphStyle=None

# table stuff


class Cell:
    def __init__(self):
        self.paragraphs: List[Paragraph] = []
        self.text: str = ''

    def add_paragraph(self, text='', style=None) -> Paragraph:
        pass


class Row:
    def __init__(self):
        self.cells: List[Cell] = []


class Column:
    def __init__(self):
        self.cells: List[Cell] = []


class Table:
    def __init__(self):
        self.rows: List[Row] = []
        self.columns: List[Column] = []

    def add_column(self, width: int) -> Column:
        pass
        # Return a _Column object of width, newly added rightmost to the table.

    def add_row(self) -> Row:
        pass
