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

    row_pattern = r"^(\d+[A-Z]?)\s+([A-Z &]+)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d+|---)\s+(\d{2})\s+([A-Z+]+)\s+(\d{2})\s+(\d{2})\s+(---|\d+)\s+(---|\d+)$"

    info = ()
    for page in pdf.pages:
        data = page.extract_text()

        for filter in filters:
            data = re.sub(filter, '', data)
        
        for line in data.splitlines():
            _match = re.match(row_pattern, line)
            if _match:
                record = info + _match.groups()
                add_record(db, record)
                continue

            _match = re.search(info_pattern, line)
            if _match:
                info = _match.groups()
                continue

            print(line)


def export_to_docx(file: str, columns_data: list[list]):
    doc = Document()

    rlen = len(columns_data[0])
    clen = len(columns_data)

    table = doc.add_table(rows=rlen, cols=clen)

    for cindex in range(clen):
        for rindex in range(rlen):
            table.cell(rindex, cindex).text = columns_data[cindex][rindex]

    doc.save(file)


def generate_database_name(length=12):
    # uuid4().hex returns a 32-character hexadecimal string (0-9, a-f)
    return f'temp_{uuid.uuid4().hex[:length]}.db'


def init_db():
    db_path = os.path.join(TEMP_DB_DIR, generate_database_name())
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
    pdf = read_pdf('sample.pdf')
    db = init_db()
    try:
        extract_tables(db, pdf)
    except Exception as e:
        print(e)
        pdf.close()
        db.close()
