"""
Utility module to handle PDF table extraction, temporary database operations,
and export functionality (DOCX) used in the PDF Data Extractor project.
"""

import pdfplumber
import re
from docx import Document
from sqlite_utils import Database
import uuid
import os
import logging
from collections import defaultdict
from io import BytesIO

# Directories for temporary file storage
TEMP_DB_DIR = 'temp/database'
TEMP_DOCX_DIR = 'temp/docx'

os.makedirs(TEMP_DB_DIR, exist_ok=True)
os.makedirs(TEMP_DOCX_DIR, exist_ok=True)

TABLE_NAME = 'score'
COLUMNS = ['seat_no', 'name', 'course_id', 'course_name', 'ise', 'ese', 'total', 'tw', 'pr', '_or', 'tut', 'tot', 'crd', 'grd', 'gp', 'cp']

logging.getLogger("pdfminer").setLevel(logging.ERROR)

class File:
    """
    Represents an uploaded PDF file and its associated temporary SQLite database.

    Attributes:
        file (BytesIO): The PDF file data.
        id (str): Unique identifier for the file.
        database_path (str): Path to the temporary SQLite database.
        database (Database): The SQLite database instance for this file.
        progress (float): Progress percentage of the PDF processing.
    """
    def __init__(self, file: BytesIO) -> None:
        self.file = file
        self.id = generate_file_id()
        self.database_path = os.path.join(TEMP_DB_DIR, generate_file_name('db'))
        init_database(self.database_path)
        
        self.progress: int = 0
    
    def __del__(self) -> None:
        # Clean up resources by closing file and deleting the temporary database.
        del self.file
        self.database.close()
        if os.path.exists(self.database_path):
            os.remove(self.database_path)
    
    def get_bytes(self) -> BytesIO:
        """Returns the stored PDF file as a BytesIO object."""
        return self.file

    def get_id(self) -> str:
        """Returns the unique identifier for the file."""
        return self.id

    def get_database_path(self) -> str:
        """Returns the filesystem path of the temporary SQLite database."""
        return self.database_path

    def get_progress(self) -> int:
        """Returns the current processing progress as a percentage."""
        return self.progress
    
    def update_progress(self, total: int, current: int) -> None:
        """
        Updates the processing progress.
        
        Args:
            total: Total number of pages in the PDF.
            current: The current page number being processed.
        """
        self.progress = int((current / total) * 100)


def extract_tables(file: File) -> None:
    """
    Extracts table data from a PDF file and stores it in a temporary SQLite database.
    
    The function reads each page of the PDF, cleans the text using regex filters,
    extracts academic records, and writes the data into the database.
    
    Args:
        file: Instance of File containing the PDF data.
    """
    pdf = pdfplumber.open(file.get_bytes())
    database = Database(file.get_database_path())

    # Regex filters to remove unwanted characters and strings.
    filters = [
        r"#|\$|\*|\(|\)|\[|\]|%|\.|\,|/\d\d\d",
        r"COURSE NAME ISE ESE TOTAL TW PR OR TUT Tot Crd Grd GP CP P&R ORD"
    ]
    info_pattern = r"SEAT NO:\s(\w+)\sNAME\s:\s([A-Z]+\s[A-Z]+\s[A-Z]+)"
    row_pattern = r"^(\d+[A-Z]?)\s+([A-Z: &]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z+]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)"

    info = ()  # Holds additional information extracted from the PDF (e.g., seat number and name).
    pages = pdf.pages
    total_pages = len(pages)
    for page_no, page in enumerate(pages, start=1):
        data = page.extract_text()

        # Clean data using filters.
        for regex_filter in filters:
            data = re.sub(regex_filter, '', data)
        
        # Process each line in the page.
        for line in data.splitlines():
            # Try to match a table row.
            if _match := re.match(row_pattern, line):
                record = info + tuple(val.strip() if val.strip() != '---' else None for val in _match.groups())
                # Convert to a dictionary and insert into the database.
                record_dict = {col: val for col, val in zip(COLUMNS, record)}
                database[TABLE_NAME].insert(record_dict)
            # Extract additional information.
            elif _match := re.search(info_pattern, line):
                info = tuple(val.strip() for val in _match.groups())
        
        file.update_progress(total_pages, page_no)
    
    pdf.close()
    database.close()


def export_as_docx(file: File, queries: list[tuple]) -> str:
    """
    Exports selected data from the PDF (stored in the SQLite database) to a DOCX file.
    
    Args:
        file: Instance of File with PDF and database data.
        queries: List of tuples where each tuple contains (course_name, column) to export.
    
    Returns:
        The file path to the generated DOCX document.
    """
    database = Database(file.get_database_path())
    doc = Document()
    docx_file_path = os.path.join(TEMP_DOCX_DIR, generate_file_name('docx'))

    seat_no_column = database.query(f"SELECT DISTINCT seat_no FROM {TABLE_NAME}")
    name_column = database.query(f"SELECT DISTINCT name FROM {TABLE_NAME}")

    # Create table header row with "SEAT NO" and "NAME".
    table = doc.add_table(rows=1, cols=len(queries) + 2)
    table.cell(0, 0).text = 'SEAT NO'
    table.cell(0, 0).paragraphs[0].runs[0].bold = True
    table.cell(0, 1).text = 'NAME'
    table.cell(0, 1).paragraphs[0].runs[0].bold = True
    
    # Add student data rows.
    for i, (seat_no, name) in enumerate(zip(seat_no_column, name_column), 1):
        table.add_row().cells[0].text = seat_no['seat_no']
        table.cell(i, 1).text = name['name']
    
    # Map seat numbers to their corresponding row in the DOCX table.
    seatno_row_map = { row.cells[0].text: row for row in table.rows[1:] }

    # Append each selected course/column to the DOCX table.
    for i, (course_name, column) in enumerate(queries, 2):
        table.cell(0, i).text = f'{course_name} ({column})'
        table.cell(0, i).paragraphs[0].runs[0].bold = True

        q = f"SELECT seat_no, {column} FROM {TABLE_NAME} WHERE course_name = '{course_name}' AND {column} != '---'"
        values = database.execute(q)

        for seat_no, value in values:
            if seat_no in seatno_row_map:
                seatno_row_map[seat_no].cells[i].text = value

    database.close()
    doc.save(docx_file_path)
    return docx_file_path


def generate_id(length: int = 12) -> str:
    """
    Generates a unique identifier from UUID4.
    
    Args:
        length: Length of the returned hexadecimal string.
    
    Returns:
        A unique hexadecimal string of the specified length.
    """
    return uuid.uuid4().hex[:length]


def generate_file_name(ext: str) -> str:
    """
    Creates a temporary file name with the given extension.
    
    Args:
        ext: The file extension (e.g., 'docx' or 'db').
    
    Returns:
        A string representing a temporary file name.
    """
    return f"temp_{generate_id()}.{ext}"


def generate_file_id() -> str:
    """
    Generates a unique identifier for an uploaded file.
    
    Returns:
        A string representing a unique file ID.
    """
    return f'file_{generate_id()}'


def init_database(file_path: str) -> None:
    """
    Initializes a new SQLite database with the required table structure.
    
    Args:
        file_path: The path where the SQLite database file will be created.
    
    Returns:
        An instance of the initialized SQLite Database.
    """
    database = Database(file_path)
    columns = {"id": int, **{col: str for col in COLUMNS}}
    database[TABLE_NAME].create(columns, pk="id")
    database.close()


def get_course_list(database_path: str) -> dict[str, list]:
    """
    Retrieves a list of available courses and their columns from the database.
    
    Args:
        database_path: The file path of the SQLite database.
    
    Returns:
        A dictionary with course names as keys and lists of column names as values.
    """
    database = Database(database_path)
    course_list: dict[str, list] = defaultdict(list)
    course_names = [course['course_name'] for course in database.query('SELECT DISTINCT course_name FROM score')]
    for name in course_names:
        for column in COLUMNS[4:]:
            has_null = database[TABLE_NAME].count_where(f"{column} IS NULL AND course_name = '{name}'") > 0
            if not has_null:
                course_list[name].append(column)
    
    database.close() 
    return course_list
