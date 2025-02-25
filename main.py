from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QLabel, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt
import sys
import pysrt

class SubtitleTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Subtitle Translator")
        self.setGeometry(300, 200, 900, 600)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        main_layout = QVBoxLayout()

        self.label = QLabel("Select a subtitle file (SRT):")
        self.label.setFont(QFont("Arial", 14))
        main_layout.addWidget(self.label)

        self.btn_select = QPushButton("Choose File")
        self.btn_select.setFont(QFont("Arial", 12))
        self.btn_select.setStyleSheet("background-color: #2980b9; color: white; padding: 12px; border-radius: 8px;")
        self.btn_select.clicked.connect(self.select_file)
        main_layout.addWidget(self.btn_select)

        self.language_label = QLabel("Select Target Language:")
        self.language_label.setFont(QFont("Arial", 14))
        main_layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.setFont(QFont("Arial", 12))
        self.language_combo.setStyleSheet("background-color: #34495e; color: white; padding: 6px; border-radius: 5px;")
        self.language_combo.addItems(["English", "French", "German", "Spanish", "Persian", "Chinese", "Japanese"])
        main_layout.addWidget(self.language_combo)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Time", "Original", "Translated"])
        self.table.setStyleSheet("background-color: #ecf0f1; color: black; border: 1px solid #ccc; padding: 5px;")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Make columns resize to window
        self.table.horizontalHeader().setDefaultSectionSize(220)  # Increase column width
        self.table.verticalHeader().setDefaultSectionSize(45)  # Increase row height
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)  # Enable direct editing
        main_layout.addWidget(self.table)

        self.btn_translate = QPushButton("Translate and Save")
        self.btn_translate.setFont(QFont("Arial", 12))
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.btn_translate.clicked.connect(self.translate_subtitle)
        main_layout.addWidget(self.btn_translate)

        self.setLayout(main_layout)

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Subtitle File", "", "Subtitle Files (*.srt)", options=options)
        if file_path:
            subs = pysrt.open(file_path)
            self.table.setRowCount(len(subs))
            for i, sub in enumerate(subs):
                self.table.setItem(i, 0, QTableWidgetItem(f"{sub.start} --> {sub.end}"))
                self.table.setItem(i, 1, QTableWidgetItem(sub.text))
                self.table.setItem(i, 2, QTableWidgetItem(""))  # Placeholder for translated text (editable)

    def translate_subtitle(self):
        QMessageBox.information(self, "Info", "Translation functionality will be implemented later.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubtitleTranslatorApp()
    window.show()
    sys.exit(app.exec_())
