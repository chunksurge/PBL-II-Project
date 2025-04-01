import pdfplumber
import re
from docx import Document
from sqlite_utils import Database
import uuid
import os
import logging

TEMP_DB_DIR = 'database'
TABLE_NAME = 'score'

logging.getLogger("pdfminer").setLevel(logging.ERROR)


def read_pdf(file) -> pdfplumber.PDF:
    pdf = pdfplumber.open(file, raise_unicode_errors=False)
    return pdf


def extract_tables(db, pdf):
    filters = [
            r"#|\$|\*|\(|\)|\[|\]|%|\.|\,|/\d\d\d",
            r"COURSE NAME ISE ESE TOTAL TW PR OR TUT Tot Crd Grd GP CP P&R ORD"
        ]
    info_pattern = r"SEAT NO:\s(\w+)\sNAME\s:\s([A-Z]+\s[A-Z]+\s[A-Z]+)"

    row_pattern = r"^(\d+[A-Z]?)\s+([A-Z: &]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z+]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(---|\d+|[A-Z]+)\s+(---|\d+|[A-Z]+)$"

    info = ()
    for page in pdf.pages:
        data = page.extract_text()

        for filter in filters:
            data = re.sub(filter, '', data)
        
        for line in data.splitlines():
            _match = re.match(row_pattern, line)
            if _match:
                record = info + tuple(val.strip() for val in _match.groups())
                add_record(db, record)
                continue

            _match = re.search(info_pattern, line)
            if _match:
                info = tuple(val.strip() for val in _match.groups())
                continue


def export(file: str, db, *queries):
    data = list()

    data.append(list(ele.values() for ele in db.query(f"SELECT DISTINCT seat_no FROM {TABLE_NAME}")))
    data.append(list(ele.values() for ele in db.query(f"SELECT DISTINCT name FROM {TABLE_NAME}")))

    for key, column in queries:
        data.append(list(ele.values() for ele in db[TABLE_NAME].rows_where(f"course_name = ? AND {column} != '---'", [key], select=column)))

    doc = Document()

    rlen = len(data[0])
    clen = len(data)

    table = doc.add_table(rows=rlen, cols=clen)
    
    table.cell(0, 0).text = 'SEAT NO'
    table.cell(0, 0).paragraphs[0].runs[0].bold = True
    table.cell(0, 1).text = 'NAME'
    table.cell(0, 1).paragraphs[0].runs[0].bold = True

    for i, ele in enumerate(queries, 2):
        table.cell(0, i).text = f'{ele[0]} ({ele[1]})'
        table.cell(0, i).paragraphs[0].runs[0].bold = True

    for cindex in range(0, clen):
        for rindex in range(1, rlen):
            table.cell(rindex, cindex).text = data[cindex][rindex]

    doc.save(file)


def generate_database_name(length=12):
    # uuid4().hex returns a 32-character hexadecimal string (0-9, a-f)
    return f'temp_{uuid.uuid4().hex[:length]}.db'


def init_db():
    db_path = os.path.join(TEMP_DB_DIR, generate_database_name())
    os.makedirs(TEMP_DB_DIR, exist_ok=True)
    
    db = Database(db_path)
    
    db[TABLE_NAME].create({
            "id": int,
            'seat_no': str,
            'name': str,
            'course_id': str,
            'course_name': str,
            'ise': str,
            'ese': str,
            'total': str,
            'tw': str,
            'pr': str,
            'or': str,
            'tut': str,
            'tot': str,
            'crd': str,
            'grd': str,
            'gp': str,
            'cp': str,
            'par': str,
            'ord': str
        }, pk="id")

    return db


def add_record(db, record):
    db[TABLE_NAME].insert({
        'seat_no': record[0],
        'name': record[1],
        'course_id': record[2],
        'course_name': record[3],
        'ise': record[4],
        'ese': record[5],
        'total': record[6],
        'tw': record[7],
        'pr': record[8],
        'or': record[9],
        'tut': record[10],
        'tot': record[11],
        'crd': record[12],
        'grd': record[13],
        'gp': record[14],
        'cp': record[15],
        'par': record[16],
        'ord': record[17]
    })


if __name__ == '__main__':
    # pdf = read_pdf('sample.pdf')
    # db = init_db()
    # try:
    #     extract_tables(db, pdf)
    #     db.close()
    #     pdf.close()
    # except Exception as e:
    #     print(e)
    #     pdf.close()
    #     db.close()

    export('sample.docx', Database('database/temp_9395fcb3de5e.db'), ('ENGINEERING MATHEMATICS III', 'ise'), ('DATA STUCTURES LABORATORY', 'tw'))
