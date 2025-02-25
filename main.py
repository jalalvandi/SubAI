from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QProgressDialog, QDialog, 
                             QLineEdit, QFormLayout, QMenuBar)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import pysrt
import google.generativeai as genai
import os
import json

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 250)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        layout = QFormLayout()

        self.api_key_input = QLineEdit(self)
        self.api_key_input.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.api_key_input.setFont(QFont("Tahoma", 10))
        layout.addRow("API Key:", self.api_key_input)

        self.http_proxy_input = QLineEdit(self)
        self.http_proxy_input.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.http_proxy_input.setFont(QFont("Tahoma", 10))
        layout.addRow("HTTP Proxy (e.g., http://127.0.0.1:8086):", self.http_proxy_input)

        self.https_proxy_input = QLineEdit(self)
        self.https_proxy_input.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.https_proxy_input.setFont(QFont("Tahoma", 10))
        layout.addRow("HTTPS Proxy (e.g., http://127.0.0.1:8086):", self.https_proxy_input)

        self.save_button = QPushButton("Save Settings")
        self.save_button.setFont(QFont("Tahoma", 10))
        self.save_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.load_existing_settings()

    def load_existing_settings(self):
        # Load existing settings from config.json if it exists
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as config_file:
                    config = json.load(config_file)
                self.api_key_input.setText(config.get('api_key', ''))
                if 'proxy' in config:
                    self.http_proxy_input.setText(config['proxy'].get('http', ''))
                    self.https_proxy_input.setText(config['proxy'].get('https', ''))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading settings: {str(e)}")

    def save_settings(self):
        # Save settings to config.json
        config = {
            "api_key": self.api_key_input.text(),
            "proxy": {
                "http": self.http_proxy_input.text(),
                "https": self.https_proxy_input.text()
            }
        }
        try:
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving settings: {str(e)}")

class TranslationWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    translated = pyqtSignal(int, str)
    error = pyqtSignal(str)

    def __init__(self, table, target_language):
        super().__init__()
        self.table = table
        self.target_language = target_language
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def run(self):
        # Run translation in a separate thread
        try:
            total_rows = self.table.rowCount()
            for row in range(total_rows):
                original_text = self.table.item(row, 1).text()
                if original_text:
                    prompt = f"Translate this text to {self.target_language} without articulation: {original_text}"
                    response = self.model.generate_content(prompt)
                    translated_text = response.text
                    self.translated.emit(row, translated_text)
                self.progress.emit(row + 1)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class SubtitleTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.initUI()

    def load_config(self):
        # Load configuration from config.json or prompt for settings
        try:
            if not os.path.exists('config.json'):
                self.open_settings_dialog()
            with open('config.json', 'r') as config_file:
                config = json.load(config_file)
            
            if 'proxy' in config:
                if 'http' in config['proxy']:
                    os.environ["HTTP_PROXY"] = config['proxy']['http']
                if 'https' in config['proxy']:
                    os.environ["HTTPS_PROXY"] = config['proxy']['https']
            
            api_key = config.get('api_key', '')
            if not api_key:
                raise ValueError("API key not found in config.json!")
            genai.configure(api_key=api_key)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading configuration: {str(e)}")
            self.open_settings_dialog()

    def initUI(self):
        self.setWindowTitle("Subtitle Translator")
        self.setGeometry(300, 200, 900, 600)
        self.setStyleSheet("background-color: #2c3e50; color: white;")

        # Add menu bar
        menu_bar = QMenuBar(self)
        menu_bar.setFont(QFont("Tahoma", 10))
        file_menu = menu_bar.addMenu("File")
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings_dialog)

        main_layout = QVBoxLayout()
        main_layout.setMenuBar(menu_bar)

        self.label = QLabel("Select a subtitle file (SRT):")
        self.label.setFont(QFont("Tahoma", 12))
        main_layout.addWidget(self.label)

        self.btn_select = QPushButton("Choose File")
        self.btn_select.setFont(QFont("Tahoma", 10))
        self.btn_select.setStyleSheet("background-color: #2980b9; color: white; padding: 12px; border-radius: 8px;")
        self.btn_select.clicked.connect(self.select_file)
        main_layout.addWidget(self.btn_select)

        self.language_label = QLabel("Select Target Language:")
        self.language_label.setFont(QFont("Tahoma", 12))
        main_layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.setFont(QFont("Tahoma", 10))
        self.language_combo.setStyleSheet("background-color: #34495e; color: white; padding: 6px; border-radius: 5px;")
        self.language_combo.addItems(["English", "French", "German", "Spanish", "Persian", "Chinese", "Japanese"])
        main_layout.addWidget(self.language_combo)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Time", "Original", "Translated"])
        self.table.setStyleSheet("background-color: #ecf0f1; color: black; border: 1px solid #ccc; padding: 0px;")
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setDefaultSectionSize(220)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        self.table.setFont(QFont("Tahoma", 10))
        main_layout.addWidget(self.table)

        self.btn_translate = QPushButton("Translate and Save")
        self.btn_translate.setFont(QFont("Tahoma", 10))
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.btn_translate.clicked.connect(self.translate_subtitle)
        main_layout.addWidget(self.btn_translate)

        self.setLayout(main_layout)

    def open_settings_dialog(self):
        # Open the settings dialog
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.load_config()

    def select_file(self):
        # Select and load an SRT file
        try:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Subtitle File", "", "Subtitle Files (*.srt)", options=options)
            if file_path:
                subs = pysrt.open(file_path)
                if not subs:
                    raise ValueError("Empty or invalid subtitle file")
                self.table.setRowCount(len(subs))
                for i, sub in enumerate(subs):
                    self.table.setItem(i, 0, QTableWidgetItem(f"{sub.start} --> {sub.end}"))
                    self.table.setItem(i, 1, QTableWidgetItem(sub.text))
                    self.table.setItem(i, 2, QTableWidgetItem(""))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading subtitle file: {str(e)}")

    def translate_subtitle(self):
        # Start the translation process
        target_language = self.language_combo.currentText()
        total_rows = self.table.rowCount()
        
        if total_rows == 0:
            QMessageBox.warning(self, "Error", "No subtitles selected for translation!")
            return

        self.progress_dialog = QProgressDialog("Translating...", "Cancel", 0, total_rows, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)

        self.worker = TranslationWorker(self.table, target_language)
        self.worker.progress.connect(self.update_progress)
        self.worker.translated.connect(self.update_translation)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.start()

    def update_progress(self, value):
        # Update the progress dialog
        self.progress_dialog.setValue(value)

    def update_translation(self, row, text):
        # Update the translated text in the table
        self.table.setItem(row, 2, QTableWidgetItem(text))

    def on_translation_finished(self):
        # Handle translation completion
        self.progress_dialog.close()
        self.save_translated_file()
        QMessageBox.information(self, "Success", "Subtitles translated successfully!")

    def on_translation_error(self, error_message):
        # Handle translation errors
        self.progress_dialog.close()
        QMessageBox.warning(self, "Error", f"Translation error: {error_message}")

    def save_translated_file(self):
        # Save the translated subtitles to a file
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Translated Subtitle", "", "Subtitle Files (*.srt)")
            if file_path:
                subs = pysrt.SubRipFile()
                for row in range(self.table.rowCount()):
                    time_text = self.table.item(row, 0).text()
                    start, end = time_text.split(' --> ')
                    text = self.table.item(row, 2).text() or self.table.item(row, 1).text()
                    sub = pysrt.SubRipItem(index=row+1, start=start, end=end, text=text)
                    subs.append(sub)
                subs.save(file_path)
                QMessageBox.information(self, "Success", "Translated file saved successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SubtitleTranslatorApp()
    window.show()
    sys.exit(app.exec_())