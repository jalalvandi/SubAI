from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QProgressBar, QDialog, 
                             QLineEdit, QFormLayout, QMenuBar, QHBoxLayout)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
import pysrt
import google.generativeai as genai
import os
import json
import time

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setGeometry(200, 200, 400, 250)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.setWindowIcon(QIcon("logo.png"))

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
            with open('config.json', 'r') as config_file:
                existing_config = json.load(config_file)
            config.update({k: v for k, v in existing_config.items() if k not in config})
        except FileNotFoundError:
            pass
        try:
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving settings: {str(e)}")

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Settings")
        self.setGeometry(200, 200, 400, 200)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        self.setWindowIcon(QIcon("logo.png"))

        layout = QFormLayout()

        self.rpm_input = QLineEdit(self)
        self.rpm_input.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.rpm_input.setFont(QFont("Tahoma", 10))
        self.rpm_input.setText("15")  # Default to 15 RPM
        layout.addRow("Requests per Minute (RPM):", self.rpm_input)

        self.model_combo = QComboBox(self)
        self.model_combo.setStyleSheet("background-color: #34495e; color: white; padding: 6px; border-radius: 5px;")
        self.model_combo.setFont(QFont("Tahoma", 10))
        self.model_combo.addItems(["gemini-1.5-flash"])  # Add more models here if needed
        layout.addRow("Model:", self.model_combo)

        self.save_button = QPushButton("Save Advanced Settings")
        self.save_button.setFont(QFont("Tahoma", 10))
        self.save_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.load_existing_settings()

    def load_existing_settings(self):
        # Load existing advanced settings from config.json if it exists
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as config_file:
                    config = json.load(config_file)
                self.rpm_input.setText(str(config.get('rpm', 15)))
                model = config.get('model', 'gemini-1.5-flash')
                if model in [self.model_combo.itemText(i) for i in range(self.model_combo.count())]:
                    self.model_combo.setCurrentText(model)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading advanced settings: {str(e)}")

    def save_settings(self):
        # Save advanced settings to config.json
        try:
            rpm = int(self.rpm_input.text())
            if rpm <= 0:
                raise ValueError("RPM must be a positive number!")
            config = {
                "rpm": rpm,
                "model": self.model_combo.currentText()
            }
            try:
                with open('config.json', 'r') as config_file:
                    existing_config = json.load(config_file)
                config.update({k: v for k, v in existing_config.items() if k not in config})
            except FileNotFoundError:
                pass
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            QMessageBox.information(self, "Success", "Advanced settings saved successfully!")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving advanced settings: {str(e)}")

class TranslationWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    translated = pyqtSignal(int, str)
    error = pyqtSignal(str)
    canceled = pyqtSignal()

    def __init__(self, table, target_language, start_row=0):
        super().__init__()
        self.table = table
        self.target_language = target_language
        self.start_row = start_row  # Starting row for translation
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        self.model = genai.GenerativeModel(config.get('model', 'gemini-1.5-flash'))
        self.rpm = config.get('rpm', 15)  # Default to 15 RPM if not set
        self.delay = 60 / self.rpm  # Calculate delay in seconds
        self.is_canceled = False
        self.current_row = start_row  # Track current row for cancellation

    def run(self):
        # Run translation in a separate thread with rate limiting
        try:
            total_rows = self.table.rowCount()
            for row in range(self.start_row, total_rows):
                if self.is_canceled:
                    self.canceled.emit()
                    return
                original_text = self.table.item(row, 1).text()
                if original_text:
                    prompt = f"Translate this text to {self.target_language} and return only the translated text without any explanation or additional content: {original_text}"
                    response = self.model.generate_content(prompt)
                    translated_text = response.text
                    self.translated.emit(row, translated_text)
                self.progress.emit(row + 1)
                self.current_row = row + 1
                if row < total_rows - 1:  # No delay after the last request
                    time.sleep(self.delay)  # Respect the RPM limit
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

    def cancel(self):
        # Cancel the translation process
        self.is_canceled = True

class SubtitleTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.load_config()
        self.initUI()
        self.worker = None
        self.last_processed_row = 0  # Track the last processed row for resuming

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
        self.setWindowIcon(QIcon("logo.png"))

        # Add menu bar
        menu_bar = QMenuBar(self)
        menu_bar.setFont(QFont("Tahoma", 10))
        file_menu = menu_bar.addMenu("File")
        settings_action = file_menu.addAction("Settings")
        settings_action.triggered.connect(self.open_settings_dialog)
        advanced_settings_action = file_menu.addAction("Advanced Settings")
        advanced_settings_action.triggered.connect(self.open_advanced_settings_dialog)

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

        # Label to display the current file name
        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setFont(QFont("Tahoma", 10))
        self.file_name_label.setStyleSheet("color: #ecf0f1;")
        main_layout.addWidget(self.file_name_label)

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

        self.btn_translate = QPushButton("Start Translate")
        self.btn_translate.setFont(QFont("Tahoma", 10))
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.btn_translate.clicked.connect(self.translate_subtitle)
        main_layout.addWidget(self.btn_translate)

        # Progress bar and control buttons layout
        self.progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(QFont("Tahoma", 10))
        self.progress_bar.setVisible(False)
        self.progress_layout.addWidget(self.progress_bar)

        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setFont(QFont("Tahoma", 10))
        self.btn_stop.setStyleSheet("background-color: #e74c3c; color: white; padding: 10px; border-radius: 8px;")
        self.btn_stop.clicked.connect(self.stop_translation)
        self.btn_stop.setVisible(False)
        self.progress_layout.addWidget(self.btn_stop)

        self.btn_resume = QPushButton("Resume")
        self.btn_resume.setFont(QFont("Tahoma", 10))
        self.btn_resume.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        self.btn_resume.clicked.connect(self.resume_translation)
        self.btn_resume.setVisible(False)
        self.progress_layout.addWidget(self.btn_resume)

        self.btn_save_partial = QPushButton("Save")
        self.btn_save_partial.setFont(QFont("Tahoma", 10))
        self.btn_save_partial.setStyleSheet("background-color: #2980b9; color: white; padding: 10px; border-radius: 8px;")
        self.btn_save_partial.clicked.connect(self.save_translated_file)
        self.btn_save_partial.setVisible(False)
        self.progress_layout.addWidget(self.btn_save_partial)

        main_layout.addLayout(self.progress_layout)
        self.setLayout(main_layout)

    def reset_translation_state(self):
        # Reset the translation state when a new file is loaded
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
        self.worker = None
        self.last_processed_row = 0  # Reset last processed row
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")

    def open_settings_dialog(self):
        # Open the basic settings dialog
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.load_config()

    def open_advanced_settings_dialog(self):
        # Open the advanced settings dialog
        dialog = AdvancedSettingsDialog(self)
        dialog.exec_()

    def select_file(self):
        # Select and load an SRT file, reset translation state
        self.reset_translation_state()
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
                # Update file name label
                self.file_name_label.setText(f"Current file: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading subtitle file: {str(e)}")
            self.file_name_label.setText("No file selected")

    def translate_subtitle(self):
        # Start the translation process
        if self.worker and self.worker.isRunning():
            return  # Prevent restarting if translation is already in progress

        target_language = self.language_combo.currentText()
        total_rows = self.table.rowCount()
        
        if total_rows == 0:
            QMessageBox.warning(self, "Error", "No subtitles selected for translation!")
            return

        self.progress_bar.setMaximum(total_rows)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.btn_stop.setVisible(True)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(False)
        self.btn_translate.setStyleSheet("background-color: #7f8c8d; color: white; padding: 12px; border-radius: 8px;")

        self.worker = TranslationWorker(self.table, target_language)
        self.worker.progress.connect(self.update_progress)
        self.worker.translated.connect(self.update_translation)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.canceled.connect(self.on_translation_canceled)
        self.worker.start()

    def resume_translation(self):
        # Resume the translation process from the last processed row
        if self.worker and self.worker.isRunning():
            return  # Prevent restarting if translation is already in progress

        target_language = self.language_combo.currentText()
        total_rows = self.table.rowCount()
        
        self.progress_bar.setMaximum(total_rows)
        self.progress_bar.setValue(self.last_processed_row)
        self.progress_bar.setVisible(True)
        self.btn_stop.setVisible(True)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(False)
        self.btn_translate.setStyleSheet("background-color: #7f8c8d; color: white; padding: 12px; border-radius: 8px;")

        self.worker = TranslationWorker(self.table, target_language, self.last_processed_row)
        self.worker.progress.connect(self.update_progress)
        self.worker.translated.connect(self.update_translation)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.canceled.connect(self.on_translation_canceled)
        self.worker.start()

    def stop_translation(self):
        # Stop the ongoing translation
        if self.worker:
            self.worker.cancel()
            self.last_processed_row = self.worker.current_row  # Save the current row when stopping

    def update_progress(self, value):
        # Update the progress bar
        self.progress_bar.setValue(value)

    def update_translation(self, row, text):
        # Update the translated text in the table
        self.table.setItem(row, 2, QTableWidgetItem(text))

    def on_translation_finished(self):
        # Handle translation completion
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.save_translated_file()
        QMessageBox.information(self, "Success", "Subtitles translated successfully!")
        self.worker = None
        self.last_processed_row = 0  # Reset after completion

    def on_translation_canceled(self):
        # Handle translation cancellation
        self.progress_bar.setVisible(True)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(True)
        self.btn_save_partial.setVisible(True)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.worker = None

    def on_translation_error(self, error_message):
        # Handle translation errors
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        QMessageBox.warning(self, "Error", f"Translation error: {error_message}")
        self.worker = None
        self.last_processed_row = 0  # Reset on error

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