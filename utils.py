import re
from docx import Document
import pdfplumber
import logging

logging.getLogger("pdfminer").setLevel(logging.ERROR)

pdf_filters = [
    r"#|\$|\*|\(|\)|\[|\]|%|\.|\,|/\d\d\d",
    r"COURSE NAME ISE ESE TOTAL TW PR OR TUT Tot Crd Grd GP CP PR ORD"
]

pdf_substitutions = {
    r'\sAB\s': ' -- ',
    r'\sAB\s': ' -- ',
    r'\s--\s': ' --- ',
    r'\s--\s': ' --- '
}

pdf_patterns = {
    'name': r"NAME\s:\s([A-Z]+\s[A-Z]+\s[A-Z]+)",
    'course': r"^(\d+[A-Z]?)\s+([A-Z: &]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z+]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)\s+(\d+|---|[A-Z]+)"
}

SCORE_TYPES = ['ISE', 'ESE', 'TOTAL', 'TW', 'PR', 'OR', 'TUT', 'Tot', 'Crd', 'Grd', 'GP', 'CP', 'PAR', 'ORD']

def pdf_parser(file_path: str, filters: list[str], patterns: dict[str, str], substitutions: dict[str, str]):
    try:
        file = pdfplumber.open(file_path)
    except Exception as e:
        logging.error(e)
        yield 100, {}
    
    progress = 0
    for page_no, page in enumerate(file.pages, start=0):
        data = page.extract_text()

        for regex_filter in filters:
            data = re.sub(regex_filter, '', data)
            
        for sub, val in substitutions.items():
            data = re.sub(sub, val, data)
        
        lines = data.splitlines()
        lines_count = len(lines)
        for line_no, line in enumerate(lines, start=1):
            for key, pattern in patterns.items():
                if _match := re.search(pattern, line):
                        if len(_match.groups()) == 1:
                            yield progress, {key: _match.group(1)}
                        else:
                            yield progress, {key: tuple(val.strip() for val in _match.groups())}
    
            progress = round((page_no * line_no) / (len(file.pages) * lines_count) * 100, 2)

    file.close()
    yield 100, {}

def export_to_docx(file_path: str, result: dict, options: tuple):
    doc = Document()
    table = doc.add_table(rows=len(result.keys()) + 1, cols=len(options) + 1)

    table.cell(0, 0).text = 'NAME'
    table.cell(0, 0).paragraphs[0].runs[0].bold = True
    for i, (course, score_type) in enumerate(options, start=1):
        table.cell(0, i).text = f'{course} ({score_type})'
        table.cell(0, i).paragraphs[0].runs[0].bold = True

    for i, (name, courses) in enumerate(result.items(), start=1):
        table.cell(i, 0).text = name
        for j, (course, score_type) in enumerate(options, start=1):
            val = courses.get(course, None)
            if val:
                table.cell(i, j).text = val[score_type]
    
    doc.save(file_path)
