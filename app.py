from flask import Flask, render_template, url_for, request, send_file
import utils
import threading
from io import BytesIO


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

files: dict[str, utils.File] = {}


@app.route('/', methods=['GET', 'POST'])
def index():
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
            pdf_file = utils.File(BytesIO(file.read()))
            files[pdf_file.get_id()] = pdf_file

            t = threading.Thread(target=utils.extract_tables, args=(pdf_file, ))
            t.start()

            return { 'file_id': pdf_file.get_id() }

    return render_template('index.html')


@app.route('/file', methods=['GET', 'POST'])
def file():
    if request.method == 'POST':
        selected_courses = request.json.get('selectedCourses')
        file = files[request.json.get('file_id')]
        
        if selected_courses:
            docx_file = utils.export_as_docx(file, [(course_name, column) for course_name, columns in selected_courses.items() for column in columns])
            return send_file(docx_file, as_attachment=True)
        
        return { 'error': 'No courses selected' }

    file_id = request.args.get('file_id')
    file = files[file_id]
    return render_template('file.html', courses=utils.get_course_list(file.get_database_path()), file_id=file.id)
