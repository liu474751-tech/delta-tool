# -*- coding: utf-8 -*-
"""
Delta Force Screen Capture Client v1.0
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QGroupBox,
    QComboBox, QSpinBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QSystemTrayIcon, QMenu, QMessageBox, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtGui import QPixmap, QAction, QPalette, QColor
from datetime import datetime

from screen_capture import ScreenCapture
from ocr_engine import OCREngine
from data_manager import DataManager
from game_detector import GameDetector


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delta Tool - Screen Capture v1.0")
        self.setMinimumSize(1000, 700)
        self.apply_dark_theme()
        
        self.screen_capture = ScreenCapture()
        self.ocr_engine = OCREngine()
        self.data_manager = DataManager()
        self.game_detector = GameDetector()
        
        self.is_monitoring = False
        self.game_detected = False
        self.current_map = None
        self.current_mode = None
        
        self.setup_ui()
        self.setup_timers()
        self.load_settings()
        
        self.statusBar().showMessage("Ready")
    
    def apply_dark_theme(self):
        self.setStyleSheet('''
            QMainWindow { background-color: #1a1a2e; }
            QWidget { background-color: #1a1a2e; color: #ffffff; }
            QGroupBox { border: 1px solid #333; border-radius: 8px; margin-top: 10px; padding-top: 10px; }
            QGroupBox::title { color: #FFD700; }
            QPushButton { background-color: #16213e; border: 1px solid #444; border-radius: 5px; padding: 8px 16px; color: white; }
            QPushButton:hover { background-color: #1f4068; border-color: #FFD700; }
            QPushButton:checked { background-color: #e94560; }
            QTabWidget::pane { border: 1px solid #333; background-color: #16213e; }
            QTabBar::tab { background-color: #1a1a2e; border: 1px solid #333; padding: 8px 20px; }
            QTabBar::tab:selected { background-color: #16213e; color: #FFD700; }
            QTableWidget { background-color: #16213e; border: 1px solid #333; }
            QTextEdit { background-color: #16213e; border: 1px solid #333; }
            QComboBox { background-color: #16213e; border: 1px solid #444; padding: 5px; }
        ''')
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Control Panel
        control_group = QGroupBox("Control Panel")
        control_layout = QHBoxLayout(control_group)
        
        self.start_btn = QPushButton("Start Monitor")
        self.start_btn.setCheckable(True)
        self.start_btn.clicked.connect(self.toggle_monitoring)
        control_layout.addWidget(self.start_btn)
        
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self.manual_capture)
        control_layout.addWidget(self.capture_btn)
        
        self.recognize_btn = QPushButton("Recognize")
        self.recognize_btn.clicked.connect(self.recognize_screen)
        control_layout.addWidget(self.recognize_btn)
        
        control_layout.addStretch()
        
        self.map_label = QLabel("Map: --")
        self.map_label.setStyleSheet("color: #FFD700;")
        control_layout.addWidget(self.map_label)
        
        self.mode_label = QLabel("Mode: --")
        self.mode_label.setStyleSheet("color: #4169E1;")
        control_layout.addWidget(self.mode_label)
        
        self.loot_label = QLabel("Profit: 0")
        self.loot_label.setStyleSheet("color: #00FF00;")
        control_layout.addWidget(self.loot_label)
        
        main_layout.addWidget(control_group)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, 1)
        
        self.setup_monitor_tab()
        self.setup_records_tab()
        self.setup_settings_tab()
        
        # Status bar
        self.game_status_label = QLabel("Game: Not Running")
        self.statusBar().addPermanentWidget(self.game_status_label)
    
    def setup_monitor_tab(self):
        monitor_widget = QWidget()
        layout = QHBoxLayout(monitor_widget)
        
        # Preview
        left_group = QGroupBox("Screen Preview")
        left_layout = QVBoxLayout(left_group)
        
        self.preview_label = QLabel("Click Start Monitor or Capture")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(640, 360)
        self.preview_label.setStyleSheet("background-color: #0f0f1a; border: 1px solid #333;")
        left_layout.addWidget(self.preview_label)
        
        layout.addWidget(left_group, 2)
        
        # Results
        right_group = QGroupBox("Recognition Results")
        right_layout = QVBoxLayout(right_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        right_layout.addWidget(self.result_text)
        
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["Item", "Count", "Value", "Time"])
        right_layout.addWidget(self.items_table)
        
        layout.addWidget(right_group, 1)
        
        self.tabs.addTab(monitor_widget, "Monitor")
    
    def setup_records_tab(self):
        records_widget = QWidget()
        layout = QVBoxLayout(records_widget)
        
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Map:"))
        self.filter_map = QComboBox()
        self.filter_map.addItems(["All", "Dam", "Longbow", "Bakshi", "Space", "Prison"])
        filter_layout.addWidget(self.filter_map)
        
        filter_layout.addWidget(QLabel("Mode:"))
        self.filter_mode = QComboBox()
        self.filter_mode.addItems(["All", "Normal", "Secret", "Top Secret", "Adaptive"])
        filter_layout.addWidget(self.filter_mode)
        
        filter_layout.addStretch()
        
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_records)
        filter_layout.addWidget(export_btn)
        
        layout.addLayout(filter_layout)
        
        self.records_table = QTableWidget()
        self.records_table.setColumnCount(7)
        self.records_table.setHorizontalHeaderLabels(
            ["DateTime", "Map", "Mode", "Zone", "Items", "Value", "Result"]
        )
        layout.addWidget(self.records_table)
        
        self.tabs.addTab(records_widget, "Records")
    
    def setup_settings_tab(self):
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)
        
        ocr_group = QGroupBox("OCR Settings")
        ocr_layout = QVBoxLayout(ocr_group)
        
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("Interval (sec):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(3)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        ocr_layout.addLayout(interval_layout)
        
        self.auto_recognize_check = QCheckBox("Auto recognize")
        self.auto_recognize_check.setChecked(True)
        ocr_layout.addWidget(self.auto_recognize_check)
        
        layout.addWidget(ocr_group)
        
        game_group = QGroupBox("Game Detection")
        game_layout = QVBoxLayout(game_group)
        
        self.auto_detect_check = QCheckBox("Auto detect game window")
        self.auto_detect_check.setChecked(True)
        game_layout.addWidget(self.auto_detect_check)
        
        layout.addWidget(game_group)
        layout.addStretch()
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        self.tabs.addTab(settings_widget, "Settings")
    
    def setup_timers(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.do_monitoring)
        
        self.game_detect_timer = QTimer()
        self.game_detect_timer.timeout.connect(self.check_game_status)
        self.game_detect_timer.start(5000)
    
    def toggle_monitoring(self):
        if self.start_btn.isChecked():
            self.is_monitoring = True
            self.start_btn.setText("Stop Monitor")
            interval = self.interval_spin.value() * 1000
            self.monitor_timer.start(interval)
            self.log("Monitoring started")
        else:
            self.is_monitoring = False
            self.start_btn.setText("Start Monitor")
            self.monitor_timer.stop()
            self.log("Monitoring stopped")
    
    def do_monitoring(self):
        if not self.is_monitoring:
            return
        
        screenshot = self.screen_capture.capture()
        if screenshot is not None:
            self.update_preview(screenshot)
            if self.auto_recognize_check.isChecked():
                self.recognize_screen()
    
    def manual_capture(self):
        screenshot = self.screen_capture.capture()
        if screenshot is not None:
            self.update_preview(screenshot)
            self.log("Capture completed")
    
    def update_preview(self, screenshot):
        try:
            import io
            screenshot.thumbnail((640, 360))
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            pixmap = QPixmap()
            pixmap.loadFromData(buffer.getvalue())
            self.preview_label.setPixmap(pixmap)
        except Exception as e:
            self.log(f"Preview error: {e}")
    
    def recognize_screen(self):
        self.log("Recognizing...")
        
        screenshot = self.screen_capture.get_latest()
        if screenshot is None:
            screenshot = self.screen_capture.capture()
        
        if screenshot is None:
            self.log("No screenshot available")
            return
        
        result = self.ocr_engine.recognize(screenshot)
        
        if result:
            if result.get("map"):
                self.current_map = result["map"]
                self.map_label.setText(f"Map: {self.current_map}")
                self.log(f"Map: {self.current_map}")
            
            if result.get("mode"):
                self.current_mode = result["mode"]
                self.mode_label.setText(f"Mode: {self.current_mode}")
                self.log(f"Mode: {self.current_mode}")
            
            if result.get("items"):
                for item in result["items"]:
                    self.add_item_to_table(item)
            
            if result.get("profit"):
                self.loot_label.setText(f"Profit: {result['profit']:,}")
        else:
            self.log("No game screen detected")
    
    def add_item_to_table(self, item):
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)
        self.items_table.setItem(row, 0, QTableWidgetItem(item.get("name", "")))
        self.items_table.setItem(row, 1, QTableWidgetItem(str(item.get("count", 1))))
        self.items_table.setItem(row, 2, QTableWidgetItem(str(item.get("value", 0))))
        self.items_table.setItem(row, 3, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
    
    def check_game_status(self):
        if self.auto_detect_check.isChecked():
            is_running = self.game_detector.is_game_running()
            
            if is_running and not self.game_detected:
                self.game_detected = True
                self.game_status_label.setText("Game: Running")
                self.game_status_label.setStyleSheet("color: #00FF00;")
                self.log("Game detected")
            elif not is_running and self.game_detected:
                self.game_detected = False
                self.game_status_label.setText("Game: Not Running")
                self.game_status_label.setStyleSheet("color: #888;")
    
    def export_records(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export", "game_records.csv", "CSV (*.csv)"
        )
        if file_path:
            self.data_manager.export_csv(file_path)
            self.log(f"Exported to: {file_path}")
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.result_text.append(f"[{timestamp}] {message}")
    
    def load_settings(self):
        settings = QSettings("DeltaTool", "ScreenCapture")
        self.interval_spin.setValue(settings.value("interval", 3, type=int))
        self.auto_recognize_check.setChecked(settings.value("auto_recognize", True, type=bool))
        self.auto_detect_check.setChecked(settings.value("auto_detect", True, type=bool))
    
    def save_settings(self):
        settings = QSettings("DeltaTool", "ScreenCapture")
        settings.setValue("interval", self.interval_spin.value())
        settings.setValue("auto_recognize", self.auto_recognize_check.isChecked())
        settings.setValue("auto_detect", self.auto_detect_check.isChecked())
        QMessageBox.information(self, "Settings", "Settings saved!")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(26, 26, 46))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(22, 33, 62))
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(22, 33, 62))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 215, 0))
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
