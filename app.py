"""
Main Flask application for the PDF Data Extractor project.

Routes:
- '/' for uploading PDFs and checking processing progress.
- '/file' for selecting courses and exporting data as a DOCX file.
"""

from flask import Flask, render_template, url_for, request, send_file
from io import BytesIO
import threading
import utils

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024   # Maximum upload size set to 16MB

# Dictionary to store file objects with their unique IDs.
files: dict[str, utils.File] = {}

@app.route('/', methods=['GET', 'POST'])
def index() -> object:
    """
    GET: Renders the homepage for PDF file upload.
    POST: Handles file upload and checks progress of PDF processing.
      - If a 'file_id' exists in the POST data, it returns the processing progress.
      - Otherwise, it processes the uploaded PDF file and starts table extraction in a background thread.
    """
    if request.method == 'POST':
        if 'file_id' in request.form:
            file_id = request.form['file_id']
            progress = files[file_id].get_progress()
            if progress < 100:
                return { 'progress': progress }
            else:
                return { 'progress': 100, 'redirect_url': url_for('file', file_id=file_id) }

        if 'file' not in request.files:
            return { 'error': 'No file uploaded' }

        file = request.files['file']
        if file:
            # Create a new File instance from the uploaded PDF data.
            pdf_file = utils.File(BytesIO(file.read()))
            files[pdf_file.get_id()] = pdf_file

            # Start a background thread to extract tables data from the PDF.
            t = threading.Thread(target=utils.extract_tables, args=(pdf_file,))
            t.start()

            return { 'file_id': pdf_file.get_id() }

    return render_template('index.html')


@app.route('/file', methods=['GET', 'POST'])
def file() -> object:
    """
    GET: Renders the file view page with a list of courses for the given file_id.
    POST: Processes the selected courses and returns the exported DOCX file.
    """
    if request.method == 'POST':
        selected_courses = request.json.get('selectedCourses')  # Expected to be a dict[str, list[str]]
        file_obj = files[request.json.get('file_id')]
        
        if selected_courses:
            # Build queries from selected courses and export the DOCX.
            docx_file = utils.export_as_docx(
                file_obj,
                [(course_name, column) for course_name, columns in selected_courses.items() for column in columns]
            )
            return send_file(docx_file, as_attachment=True)
        
        return { 'error': 'No courses selected' }

    file_id = request.args.get('file_id')
    file_obj = files[file_id]
    return render_template('file.html', courses=utils.get_course_list(file_obj.get_database_path()), file_id=file_obj.id)
