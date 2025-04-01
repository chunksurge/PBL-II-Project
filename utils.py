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


def extract_tables(db: Database, pdf_path: str):
    pdf = pdfplumber.open(pdf_path)

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
                add_record(db, record)
            
            elif _match := re.search(info_pattern, line):
                info = tuple(val.strip() for val in _match.groups())
        break
    pdf.close()


def export(file_path: str, db: Database, queries: list[tuple[str, str]]):
    doc = Document()

    seat_no_column = db.query(f"SELECT DISTINCT seat_no FROM {TABLE_NAME}")
    name_column = db.query(f"SELECT DISTINCT name FROM {TABLE_NAME}")

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
        values = db.execute(q)

        for seat_no, value in values:
            if seat_no in seatno_row_map:
                seatno_row_map[seat_no].cells[i].text = value

    doc.save(file_path)


def generate_temp_name(ext: str, length=12):
    # uuid4().hex returns a 32-character hexadecimal string (0-9, a-f)
    return f'temp_{uuid.uuid4().hex[:length]}.{ext}'


def init_db(file_path: str):
    db = Database(file_path)
    
    columns = { "id": int } | {col: str for col in COLUMNS}
    db[TABLE_NAME].create(columns , pk="id")

    return db


def add_record(db: Database, record: tuple[str]):
    record = {col: val for col, val in zip(COLUMNS, record)}
    db[TABLE_NAME].insert(record)


def get_course_names(db: Database):
    result = defaultdict(list)

    course_names = list(course['course_name'] for course in db.query('SELECT DISTINCT course_name FROM score'))
    for name in course_names:
        for column in COLUMNS[4:]:
            has_null = db[TABLE_NAME].count_where(f"{column} IS NULL AND course_name = '{name}'") > 0
            if not has_null:
                result[name].append(column)
    
    return result


# if __name__ == '__main__':
    # db = init_db(os.path.join(TEMP_DB_DIR, generate_temp_name('db')))
    # extract_tables(db, 'scrap/sample.pdf')
    # db.close()

    # export('sample.docx', Database('database/temp_6f16e23d77b3.db'), ('ENGINEERING MATHEMATICS III', 'ise'), ('DATA STUCTURES LABORATORY', 'tw'), ('SMART CITIES', 'tot'))

    # courses = get_course_names(Database('temp/database/temp_98acca113ba2.db'))
    # for course, val in courses.items():
    #     print(course, *val)

    # pass
