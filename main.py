import sys

from PySide6.QtWidgets import  QApplication, QMainWindow, QFileDialog, QCheckBox, QFrame, QHBoxLayout, QLabel, QWidget, QMessageBox
from PySide6.QtCore import QThread, QObject, Signal

from app import Ui_MainWindow

import utils
from collections import defaultdict
import logging

logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] - %(message)s')

class Worker(QObject):
    progress = Signal(int)
    finished = Signal(dict)

    def __init__(self, *args):
        super().__init__()
        self.args = args
    
    def export_file_data(self):
        utils.export_to_docx(*self.args)
        self.finished.emit({})

    def process_file(self):
        parser = utils.pdf_parser(*self.args, utils.pdf_filters, utils.pdf_patterns, utils.pdf_substitutions)

        result = defaultdict(dict)
        name = None
        
        for progress, data in parser:
            if progress == 100:
                self.progress.emit(100)
                self.finished.emit(result)
                return

            if data:
                if 'name' in data:
                    name = data['name']
                
                elif 'course' in data:
                    course = data['course'][1]
                    result[name][course] = {key: value for key, value in zip(utils.SCORE_TYPES, data['course'][2:])}

            self.progress.emit(progress)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.file_name.setText('No file selected')
        self.ui.process_pdf_btn.setEnabled(False)
        self.ui.progress_bar.hide()
        self.ui.course_select_widget.hide()

        self.ui.select_file_btn.clicked.connect(self.select_file)
        self.ui.process_pdf_btn.clicked.connect(self.process_file)
        self.ui.export_as_docx_btn.clicked.connect(self.export_file_data)

        self.file_path = None
        self.prev_progress = 0

        self.resize(405, 215)
    
    def show_error(self, message, submessage=None):
        error_box = QMessageBox(self)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        if submessage:
            error_box.setInformativeText(submessage)
        error_box.exec()
    
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
        parent=self,
        caption="Open File",
        filter="PDF Files (*.pdf)"
        )

        if file_path:
            self.ui.file_name.setText(f'Selected file: {file_path.split("/")[-1]}')
            self.ui.process_pdf_btn.setEnabled(True)
            self.file_path = file_path

            self.ui.course_select_widget.hide()

            while self.ui.verticalLayout_11.count():
                child = self.ui.verticalLayout_11.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            self.ui.process_pdf_btn.setEnabled(True)

    def process_file(self):
        self.prev_progress = 0
        self.ui.progress_bar.show()
        self.ui.progress_bar.setValue(0)
        self.ui.select_file_btn.setEnabled(False)
        self.ui.export_as_docx_btn.setEnabled(False)
        self.ui.process_pdf_btn.setEnabled(False)

        self.ui.process_pdf_btn.setText('Processing...')
        
        self.thread = QThread()
        self.worker = Worker(self.file_path)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.process_file)
        self.worker.finished.connect(self.process_file_done)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.progress.connect(self.update_progress)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()
    
    def update_progress(self, progress):
        progress = int(progress)
        if progress > self.prev_progress:
            self.prev_progress = progress
            self.ui.progress_bar.setValue(progress)

    def process_file_done(self, result):
        if not result:
            self.ui.file_name.setText('No file selected')
            self.ui.process_pdf_btn.setEnabled(False)
            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.hide()
            self.prev_progress = 0
            self.ui.select_file_btn.setEnabled(True)
            self.ui.process_pdf_btn.setText('Start processing')
            self.show_error('Failed to process file!', 'Possible reasons:\n- PDF file does not contain any data\n- PDF File format is not supported\n- PDF file does not exist')
            return

        self.result = result
        self.ui.progress_bar.hide()
        self.show_selected_courses()
        self.ui.course_select_widget.show()
        self.ui.select_file_btn.setEnabled(True)
        self.ui.export_as_docx_btn.setEnabled(True)
        self.ui.process_pdf_btn.setText('Start processing')
        self.adjustSize()
    
    def show_selected_courses(self):        
        self.checkBoxes = defaultdict(list)
        courses = set()
        for course in self.result.values():
            courses.update(course.keys())
        
        for course in courses:
            course_frame = QWidget()
            _layout = QHBoxLayout(course_frame)
            course_name_label = QLabel()
            course_name_label.setText(course)
            course_name_label.setWordWrap(True)

            _layout.addWidget(course_name_label)

            score_types_frame = QFrame(course_frame)
            score_types_frame.setFrameShape(QFrame.Shape.StyledPanel)
            score_types_frame.setFrameShadow(QFrame.Shadow.Raised)
            _layout_1 = QHBoxLayout(score_types_frame)

            for score_type in utils.SCORE_TYPES:
                checkbox = QCheckBox(score_types_frame)
                checkbox.setText(score_type)
                _layout_1.addWidget(checkbox)
                self.checkBoxes[course].append(checkbox)

            _layout.addWidget(score_types_frame)
            self.ui.verticalLayout_11.addWidget(course_frame)

    def export_file_data(self):
        options = []
        for course, checkboxes in self.checkBoxes.items():
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    options.append((course, checkbox.text()))

        if not options:
            return

        file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Save File",
        "document.docx",
        filter="Docx Files (*.docx)"
        )

        if file_path:
            self.ui.select_file_btn.setEnabled(False)
            self.ui.export_as_docx_btn.setEnabled(False)

            self.thread = QThread()
            self.worker = Worker(file_path, self.result, options)
            self.worker.moveToThread(self.thread)

            self.thread.started.connect(self.worker.export_file_data)
            self.worker.finished.connect(self.export_file_data_done)
            self.worker.finished.connect(self.thread.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)

            self.thread.start()
    
    def export_file_data_done(self):
        self.ui.select_file_btn.setEnabled(True)
        self.ui.export_as_docx_btn.setEnabled(True)


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
