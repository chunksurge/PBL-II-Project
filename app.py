# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'app.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QProgressBar, QPushButton, QScrollArea,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(435, 382)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.Scanner))
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"font: 500 11pt \"Ubuntu\";")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.head_widget = QWidget(self.centralwidget)
        self.head_widget.setObjectName(u"head_widget")
        self.head_widget.setMaximumSize(QSize(16777215, 80))
        self.verticalLayout_2 = QVBoxLayout(self.head_widget)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.title = QLabel(self.head_widget)
        self.title.setObjectName(u"title")
        self.title.setStyleSheet(u"font: 670 22pt \"Ubuntu Sans\";")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_2.addWidget(self.title)


        self.verticalLayout.addWidget(self.head_widget)

        self.line = QFrame(self.centralwidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.file_select_widget = QWidget(self.centralwidget)
        self.file_select_widget.setObjectName(u"file_select_widget")
        self.verticalLayout_3 = QVBoxLayout(self.file_select_widget)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.select_file_widget = QWidget(self.file_select_widget)
        self.select_file_widget.setObjectName(u"select_file_widget")
        self.horizontalLayout = QHBoxLayout(self.select_file_widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.file_name = QLabel(self.select_file_widget)
        self.file_name.setObjectName(u"file_name")
        self.file_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout.addWidget(self.file_name)

        self.select_file_btn = QPushButton(self.select_file_widget)
        self.select_file_btn.setObjectName(u"select_file_btn")
        self.select_file_btn.setMaximumSize(QSize(100, 16777215))

        self.horizontalLayout.addWidget(self.select_file_btn)


        self.verticalLayout_3.addWidget(self.select_file_widget)

        self.progress_bar = QProgressBar(self.file_select_widget)
        self.progress_bar.setObjectName(u"progress_bar")
        self.progress_bar.setValue(50)

        self.verticalLayout_3.addWidget(self.progress_bar)

        self.process_pdf_btn = QPushButton(self.file_select_widget)
        self.process_pdf_btn.setObjectName(u"process_pdf_btn")

        self.verticalLayout_3.addWidget(self.process_pdf_btn)


        self.verticalLayout.addWidget(self.file_select_widget)

        self.line_2 = QFrame(self.centralwidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.course_select_widget = QWidget(self.centralwidget)
        self.course_select_widget.setObjectName(u"course_select_widget")
        self.verticalLayout_8 = QVBoxLayout(self.course_select_widget)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.select_course_label_widget = QWidget(self.course_select_widget)
        self.select_course_label_widget.setObjectName(u"select_course_label_widget")
        self.verticalLayout_9 = QVBoxLayout(self.select_course_label_widget)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.select_course_label = QLabel(self.select_course_label_widget)
        self.select_course_label.setObjectName(u"select_course_label")
        self.select_course_label.setStyleSheet(u"font: 500 14pt \"Ubuntu\";")
        self.select_course_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_9.addWidget(self.select_course_label)


        self.verticalLayout_8.addWidget(self.select_course_label_widget)

        self.course_container_widget = QWidget(self.course_select_widget)
        self.course_container_widget.setObjectName(u"course_container_widget")
        self.verticalLayout_10 = QVBoxLayout(self.course_container_widget)
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(-1, 0, 0, 0)
        self.scroll_area = QScrollArea(self.course_container_widget)
        self.scroll_area.setObjectName(u"scroll_area")
        self.scroll_area.setWidgetResizable(True)
        self.scrollarea_widget = QWidget()
        self.scrollarea_widget.setObjectName(u"scrollarea_widget")
        self.scrollarea_widget.setGeometry(QRect(0, 0, 388, 64))
        self.verticalLayout_11 = QVBoxLayout(self.scrollarea_widget)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.scroll_area.setWidget(self.scrollarea_widget)

        self.verticalLayout_10.addWidget(self.scroll_area)


        self.verticalLayout_8.addWidget(self.course_container_widget)

        self.export_btn_widget = QWidget(self.course_select_widget)
        self.export_btn_widget.setObjectName(u"export_btn_widget")
        self.horizontalLayout_2 = QHBoxLayout(self.export_btn_widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(9, -1, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.export_as_docx_btn = QPushButton(self.export_btn_widget)
        self.export_as_docx_btn.setObjectName(u"export_as_docx_btn")
        self.export_as_docx_btn.setMaximumSize(QSize(120, 16777215))

        self.horizontalLayout_2.addWidget(self.export_as_docx_btn)


        self.verticalLayout_8.addWidget(self.export_btn_widget)


        self.verticalLayout.addWidget(self.course_select_widget)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"ScoreCraftr", None))
        self.title.setText(QCoreApplication.translate("MainWindow", u"ScoreCraftr", None))
        self.file_name.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.select_file_btn.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.process_pdf_btn.setText(QCoreApplication.translate("MainWindow", u"Start Processing", None))
        self.select_course_label.setText(QCoreApplication.translate("MainWindow", u"Select Course", None))
        self.export_as_docx_btn.setText(QCoreApplication.translate("MainWindow", u"Export as Docx", None))
    # retranslateUi

