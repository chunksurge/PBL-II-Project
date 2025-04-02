import pdfplumber
import re
from docx import Document
from sqlite_utils import Database
import uuid
import os
import logging
from collections import defaultdict

TEMP_DB_DIR = 'temp/database'
TEMP_DOCX_DIR = 'temp/docx'

os.makedirs(TEMP_DB_DIR, exist_ok=True)
os.makedirs(TEMP_DOCX_DIR, exist_ok=True)

TABLE_NAME = 'score'
COLUMNS = ['seat_no', 'name', 'course_id', 'course_name', 'ise', 'ese', 'total', 'tw', 'pr', '_or', 'tut', 'tot', 'crd', 'grd', 'gp', 'cp']

logging.getLogger("pdfminer").setLevel(logging.ERROR)


class File:
    def __init__(self, file: bytes):
        self.file = file
        self.id = generate_file_id()
        self.database_path = os.path.join(TEMP_DB_DIR, generate_file_name('db'))
        self.database = init_database(self.database_path)

        self.progress = 0
    
    def __del__(self):
        del self.file

        self.database.close()
        if os.path.exists(self.database_path):
            os.remove(self.database_path)
    
    def get_bytes(self):
        return self.file

    def get_id(self):
        return self.id

    def get_database_path(self):
        return self.database_path

    def get_database(self):
        return self.database

    def get_progress(self):
        return self.progress
    
    def update_progress(self, total, current):
        self.progress = (current / total) * 100


def extract_tables(file: File):
    pdf = pdfplumber.open(file.get_bytes())
    database = Database(file.get_database_path())

    filters = [
            r"#|\$|\*|\(|\)|\[|\]|%|\.|\,|/\d\d\d",
            r"COURSE NAME ISE ESE TOTAL TW PR OR TUT Tot Crd Grd GP CP P&R ORD"
        ]
    info_pattern = r"SEAT NO:\s(\w+)\sNAME\s:\s([A-Z]+\s[A-Z]+\s[A-Z]+)"

    row_pattern = r"^(\d+[A-Z]?)\s+([A-Z: &]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z+]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)"

    info = ()
    for page in pdf.pages:
        data = page.extract_text()

        for filter in filters:
            data = re.sub(filter, '', data)
        
        for line in data.splitlines():
            if _match := re.match(row_pattern, line):
                record = info + tuple(val.strip() if val.strip() != '---' else None for val in _match.groups())
                add_record(database, record)
            
            elif _match := re.search(info_pattern, line):
                info = tuple(val.strip() for val in _match.groups())
        
        file.update_progress(len(pdf.pages), pdf.pages.index(page) + 1)
    
    pdf.close()
    database.close()


def export_as_docx(file: File, queries: list[tuple[str, str]]):
    database = Database(file.get_database_path())
    doc = Document()
    docx_file_path = os.path.join(TEMP_DOCX_DIR, generate_file_name('docx'))

    seat_no_column = database.query(f"SELECT DISTINCT seat_no FROM {TABLE_NAME}")
    name_column = database.query(f"SELECT DISTINCT name FROM {TABLE_NAME}")

    table = doc.add_table(rows=1, cols=len(queries) + 2)
    table.cell(0, 0).text = 'SEAT NO'
    table.cell(0, 0).paragraphs[0].runs[0].bold = True
    table.cell(0, 1).text = 'NAME'
    table.cell(0, 1).paragraphs[0].runs[0].bold = True
    
    for i, (seat_no, name) in enumerate(zip(seat_no_column, name_column), 1):
        table.add_row().cells[0].text = seat_no['seat_no']
        table.cell(i, 1).text = name['name']
    
    # Build a mapping from seat_no to table row for quick lookup.
    seatno_row_map = { row.cells[0].text: row for row in table.rows[1:] }

    # Process each query and update the corresponding column in the table.
    for i, (couse_name, column) in enumerate(queries, 2):
        table.cell(0, i).text = f'{couse_name} ({column})'
        table.cell(0, i).paragraphs[0].runs[0].bold = True

        q = f"SELECT seat_no, {column} FROM {TABLE_NAME} WHERE course_name = '{couse_name}' AND {column} != '---'"
        values = database.execute(q)

        for seat_no, value in values:
            if seat_no in seatno_row_map:
                seatno_row_map[seat_no].cells[i].text = value

    database.close()
    doc.save(docx_file_path)
    return docx_file_path


def generate_id(length=12):
    # uuid4().hex returns a 32-character hexadecimal string (0-9, a-f)
    return uuid.uuid4().hex[:length]


def generate_file_name(ext):
    return f"temp_{generate_id()}.{ext}"


def generate_file_id():
    return f'file_{generate_id()}'


def init_database(file_path: str):
    database = Database(file_path)
    
    columns = { "id": int } | {col: str for col in COLUMNS}
    database[TABLE_NAME].create(columns , pk="id")

    return database


def add_record(database: Database, record: tuple[str]):
    record = {col: val for col, val in zip(COLUMNS, record)}
    database[TABLE_NAME].insert(record)


def get_course_list(database_path: str):
    database = Database(database_path)
    course_list = defaultdict(list)

    course_names = list(course['course_name'] for course in database.query('SELECT DISTINCT course_name FROM score'))
    for name in course_names:
        for column in COLUMNS[4:]:
            has_null = database[TABLE_NAME].count_where(f"{column} IS NULL AND course_name = '{name}'") > 0
            if not has_null:
                course_list[name].append(column)
    
    database.close()
    
    return course_list
