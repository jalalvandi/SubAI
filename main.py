import sys
import os
import json
import time
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QProgressBar, QDialog, 
                             QLineEdit, QFormLayout, QHBoxLayout)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import pysrt
import google.generativeai as genai
from collections import defaultdict

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Public Settings")
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
        # Load existing API key and proxy settings from config.json
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
        # Save API key and proxy settings to config.json
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
        self.setGeometry(200, 200, 400, 250)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        if os.path.exists("logo.png"):
            self.setWindowIcon(QIcon("logo.png"))

        layout = QFormLayout()

        self.rpm_input = QLineEdit(self)
        self.rpm_input.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.rpm_input.setFont(QFont("Tahoma", 10))
        self.rpm_input.setText("15")
        layout.addRow("Requests per Minute (RPM):", self.rpm_input)

        self.model_combo = QComboBox(self)
        self.model_combo.setStyleSheet("background-color: #34495e; color: white; padding: 6px; border-radius: 5px;")
        self.model_combo.setFont(QFont("Tahoma", 10))
        self.model_combo.addItems(["gemini-1.5-flash"])
        layout.addRow("Model:", self.model_combo)

        self.cache_combo = QComboBox(self)
        self.cache_combo.setStyleSheet("background-color: #34495e; color: white; padding: 6px; border-radius: 5px;")
        self.cache_combo.setFont(QFont("Tahoma", 10))
        self.cache_combo.addItems(["RAM", "File", "None"])
        self.cache_combo.setCurrentText("RAM")
        layout.addRow("Translation Cache:", self.cache_combo)

        self.save_button = QPushButton("Save Advanced Settings")
        self.save_button.setFont(QFont("Tahoma", 10))
        self.save_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 8px;")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
        self.load_existing_settings()

    def load_existing_settings(self):
        # Load advanced settings (RPM, model, cache mode) from config.json
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as config_file:
                    config = json.load(config_file)
                self.rpm_input.setText(str(config.get('rpm', 15)))
                model = config.get('model', 'gemini-1.5-flash')
                if model in [self.model_combo.itemText(i) for i in range(self.model_combo.count())]:
                    self.model_combo.setCurrentText(model)
                cache_mode = config.get('cache_mode', 'RAM')
                if cache_mode in ["RAM", "File", "None"]:
                    self.cache_combo.setCurrentText(cache_mode)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading advanced settings: {str(e)}")

    def save_settings(self):
        # Save advanced settings to config.json and initialize cache file if 'File' mode is selected
        try:
            rpm = int(self.rpm_input.text())
            if rpm <= 0:
                raise ValueError("RPM must be a positive number!")
            config = {
                "rpm": rpm,
                "model": self.model_combo.currentText(),
                "cache_mode": self.cache_combo.currentText()
            }
            try:
                with open('config.json', 'r') as config_file:
                    existing_config = json.load(config_file)
                config.update({k: v for k, v in existing_config.items() if k not in config})
            except FileNotFoundError:
                pass
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            
            if self.cache_combo.currentText() == "File" and not os.path.exists('translation_cache.json'):
                with open('translation_cache.json', 'w') as cache_file:
                    json.dump({}, cache_file, indent=4)
            
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

    def __init__(self, table, target_language, start_row=0, config=None, translation_cache=None):
        super().__init__()
        self.table = table
        self.target_language = target_language
        self.start_row = start_row
        self.config = config
        self.model = genai.GenerativeModel(self.config.get('model', 'gemini-1.5-flash'))
        self.rpm = self.config.get('rpm', 15)
        self.delay = 60 / self.rpm
        self.is_canceled = False
        self.current_row = start_row
        self.cache_mode = self.config.get('cache_mode', 'RAM')
        self.translation_cache = translation_cache if translation_cache is not None else {}

    def run(self):
        # Main translation loop handling each subtitle row
        try:
            total_rows = self.table.rowCount()
            for row in range(self.start_row, total_rows):
                if self.is_canceled:
                    self.canceled.emit()
                    return
                original_text = self.table.item(row, 1).text()
                if original_text:
                    if self.cache_mode != "None" and self.translation_cache is not None:
                        cache_key = f"{self.target_language}:{original_text}"
                        if cache_key in self.translation_cache:
                            translated_text = self.translation_cache[cache_key]
                        else:
                            prompt = f"Translate this text to {self.target_language} and return only the translated text without any explanation or additional content: {original_text}"
                            try:
                                response = self.model.generate_content(prompt)
                                translated_text = response.text
                            except (requests.exceptions.ConnectionError, Exception) as e:
                                self.error.emit("Internet connection lost. Translation stopped.")
                                self.canceled.emit()
                                return
                            self.translation_cache[cache_key] = translated_text
                            if self.cache_mode == "File":
                                self.save_cache_to_file()
                        self.translated.emit(row, translated_text)
                    else:
                        prompt = f"Translate this text to {self.target_language} and return only the translated text without any explanation or additional content: {original_text}"
                        try:
                            response = self.model.generate_content(prompt)
                            translated_text = response.text
                        except (requests.exceptions.ConnectionError, Exception) as e:
                            self.error.emit("Internet connection lost. Translation stopped.")
                            self.canceled.emit()
                            return
                        self.translated.emit(row, translated_text)
                self.progress.emit(row + 1)
                self.current_row = row + 1
                if row < total_rows - 1:
                    time.sleep(self.delay)
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Error during translation: {str(e)}")

    def cancel(self):
        # Manually cancel the translation process
        self.is_canceled = True

    def save_cache_to_file(self):
        # Save translation cache to file in 'File' mode
        try:
            with open('translation_cache.json', 'w', encoding='utf-8') as cache_file:
                json.dump(self.translation_cache, cache_file, indent=4, ensure_ascii=False)
        except Exception as e:
            QMessageBox.warning(None, "Error", f"Failed to save cache to file: {str(e)}")

class SubtitleTranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.last_processed_row = 0
        self.initUI()
        self.config = self.load_config()
        self.translation_cache = self.load_translation_cache()

    def load_config(self):
        # Load configuration from config.json or prompt for settings if not found
        try:
            if not os.path.exists('config.json'):
                self.open_settings_dialog()
                return {}
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
            return config
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading configuration: {str(e)}")
            self.open_settings_dialog()
            return {}

    def load_translation_cache(self):
        # Load translation cache based on configured cache mode
        cache_mode = self.config.get('cache_mode', 'RAM')
        if cache_mode == "File" and os.path.exists('translation_cache.json'):
            try:
                with open('translation_cache.json', 'r', encoding='utf-8') as cache_file:
                    return json.load(cache_file)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error loading cache from file: {str(e)}")
        return defaultdict(str) if cache_mode == "RAM" else {} if cache_mode == "File" else None

    def save_translation_cache(self):
        # Save translation cache to file if configured for 'File' mode
        if self.config.get('cache_mode', 'RAM') == "File" and self.translation_cache is not None:
            try:
                with open('translation_cache.json', 'w', encoding='utf-8') as cache_file:
                    json.dump(self.translation_cache, cache_file, indent=4, ensure_ascii=False)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error saving cache to file: {str(e)}")

    def clear_cache(self):
        # Clear the translation cache file if in 'File' mode
        if self.config.get('cache_mode', 'RAM') == "File":
            try:
                if os.path.exists('translation_cache.json'):
                    with open('translation_cache.json', 'w', encoding='utf-8') as cache_file:
                        json.dump({}, cache_file, indent=4)
                    self.translation_cache = {}
                    QMessageBox.information(self, "Success", "Translation cache cleared successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error clearing cache: {str(e)}")

    def initUI(self):
        # Initialize the main window UI
        self.setWindowTitle("Subtitle Translator")
        self.setGeometry(0, 0, 800, 550)
        self.setStyleSheet("background-color: #2c3e50; color: white;")
        if os.path.exists("logo.png"):
            self.setWindowIcon(QIcon("logo.png"))

        # Center the window on the screen
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

        # Top menu bar with buttons aligned to the right
        menu_layout = QHBoxLayout()
        menu_layout.addStretch()

        self.settings_button = QPushButton("Public Settings")
        self.settings_button.setFont(QFont("Tahoma", 10))
        self.settings_button.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        menu_layout.addWidget(self.settings_button)

        self.advanced_settings_button = QPushButton("Advanced Settings")
        self.advanced_settings_button.setFont(QFont("Tahoma", 10))
        self.advanced_settings_button.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.advanced_settings_button.clicked.connect(self.open_advanced_settings_dialog)
        menu_layout.addWidget(self.advanced_settings_button)

        self.clear_cache_button = QPushButton("Clear Cache")
        self.clear_cache_button.setFont(QFont("Tahoma", 10))
        self.clear_cache_button.setStyleSheet("background-color: #34495e; color: white; padding: 5px; border-radius: 5px;")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        menu_layout.addWidget(self.clear_cache_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(menu_layout)

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

        self.progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setFont(QFont("Tahoma", 10))
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
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
        # Reset the translation state and UI elements
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
        self.worker = None
        self.last_processed_row = 0
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")

    def open_settings_dialog(self):
        # Open the public settings dialog
        dialog = SettingsDialog(self)
        dialog.exec_()
        self.config = self.load_config()
        self.translation_cache = self.load_translation_cache()

    def open_advanced_settings_dialog(self):
        # Open the advanced settings dialog
        dialog = AdvancedSettingsDialog(self)
        dialog.exec_()
        self.translation_cache = self.load_translation_cache()

    def select_file(self):
        # Select and load an SRT file into the table
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
                self.file_name_label.setText(f"Current file: {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading subtitle file: {str(e)}")
            self.file_name_label.setText("No file selected")

    def translate_subtitle(self):
        # Start the translation process
        if self.worker and self.worker.isRunning():
            return

        target_language = self.language_combo.currentText()
        total_rows = self.table.rowCount()
        
        if total_rows == 0:
            QMessageBox.warning(self, "Error", "No subtitles selected for translation!")
            return

        self.progress_bar.setMaximum(total_rows)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat(f"Translating: %v/{total_rows}")
        self.btn_stop.setVisible(True)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(False)
        self.btn_translate.setStyleSheet("background-color: #7f8c8d; color: white; padding: 12px; border-radius: 8px;")

        self.worker = TranslationWorker(self.table, target_language, config=self.config, translation_cache=self.translation_cache)
        self.worker.progress.connect(self.update_progress)
        self.worker.translated.connect(self.update_translation)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.canceled.connect(self.on_translation_canceled)
        self.worker.start()

    def resume_translation(self):
        # Resume the translation process from the last processed row
        if self.worker and self.worker.isRunning():
            return

        target_language = self.language_combo.currentText()
        total_rows = self.table.rowCount()
        
        self.progress_bar.setMaximum(total_rows)
        self.progress_bar.setValue(self.last_processed_row)
        self.progress_bar.setVisible(True)
        self.progress_bar.setFormat(f"Translating: %v/{total_rows}")
        self.btn_stop.setVisible(True)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(False)
        self.btn_translate.setStyleSheet("background-color: #7f8c8d; color: white; padding: 12px; border-radius: 8px;")

        self.worker = TranslationWorker(self.table, target_language, self.last_processed_row, config=self.config, translation_cache=self.translation_cache)
        self.worker.progress.connect(self.update_progress)
        self.worker.translated.connect(self.update_translation)
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.error.connect(self.on_translation_error)
        self.worker.canceled.connect(self.on_translation_canceled)
        self.worker.start()

    def stop_translation(self):
        # Stop the ongoing translation process
        if self.worker:
            self.worker.cancel()
            self.last_processed_row = self.worker.current_row
            if self.config.get('cache_mode', 'RAM') == "File":
                self.save_translation_cache()

    def update_progress(self, value):
        # Update the progress bar value
        self.progress_bar.setValue(value)

    def update_translation(self, row, text):
        # Update the translated text in the table
        self.table.setItem(row, 2, QTableWidgetItem(text))

    def on_translation_finished(self):
        # Handle successful completion of translation
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.save_translated_file()
        QMessageBox.information(self, "Success", "Subtitles translated successfully!")
        self.worker = None
        self.last_processed_row = 0
        if self.config.get('cache_mode', 'RAM') == "File":
            self.save_translation_cache()

    def on_translation_canceled(self):
        # Handle cancellation of translation process
        self.progress_bar.setVisible(True)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(True)
        self.btn_save_partial.setVisible(True)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        self.worker = None

    def on_translation_error(self, error_message):
        # Handle errors during translation process
        self.progress_bar.setVisible(False)
        self.btn_stop.setVisible(False)
        self.btn_resume.setVisible(False)
        self.btn_save_partial.setVisible(False)
        self.btn_translate.setEnabled(True)
        self.btn_translate.setStyleSheet("background-color: #27ae60; color: white; padding: 12px; border-radius: 8px;")
        QMessageBox.warning(self, "Error", error_message)
        self.worker = None
        self.last_processed_row = 0

    def save_translated_file(self):
        # Save the translated subtitles to an SRT file
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
    # Main entry point for the application
    app = QApplication(sys.argv)
    window = SubtitleTranslatorApp()
    window.show()
    sys.exit(app.exec_())