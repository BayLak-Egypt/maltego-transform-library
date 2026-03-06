import sys
import time
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QLabel, QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from lib.styles.styles import COLORS

class GUIWorker(QThread):
    progress_update = pyqtSignal(int)
    status_update = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks

    def run(self):
        if not self.tasks:
            self.finished_signal.emit()
            return
        step_increment = 100 // len(self.tasks)
        for i, task in enumerate(self.tasks):
            self.status_update.emit(f'Loading: {task}...')
            for step in range(step_increment):
                time.sleep(0.02)
                self.progress_update.emit(i * step_increment + step + 1)
        self.progress_update.emit(100)
        self.status_update.emit('Ready!')
        time.sleep(0.5)
        self.finished_signal.emit()

class MaltegoGUILoader(QWidget):

    def __init__(self, tasks):
        super().__init__()
        self.tasks = tasks
        self.initUI()
        self.center_window()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setFixedSize(450, 150)
        self.setStyleSheet(f"\n            QWidget {{ \n                background-color: {COLORS['bg_dark']}; \n                color: {COLORS['text_main']}; \n                border: 2px solid {COLORS['accent']}; \n                font-family: 'Segoe UI'; \n                border-radius: 10px; \n            }}\n            QProgressBar {{ \n                border: 1px solid #444; \n                border-radius: 5px; \n                background-color: {COLORS['bg_card']}; \n                text-align: center; \n                height: 10px; \n                font-size: 8px; \n            }}\n            QProgressBar::chunk {{ \n                background-color: {COLORS['accent']}; \n                width: 10px; \n            }}\n        ")
        layout = QVBoxLayout()
        self.title_label = QLabel('Maltego Transform Library')
        self.title_label.setStyleSheet(f'font-weight: bold; font-size: 14px; color: {COLORS['accent']}; border: none;')
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label = QLabel('Initializing Environment...')
        self.status_label.setStyleSheet(f'border: none; font-size: 11px; color: {COLORS['text_dim']};')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pbar = QProgressBar(self)
        self.pbar.setMaximum(100)
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addSpacing(5)
        layout.addWidget(self.status_label)
        layout.addWidget(self.pbar)
        layout.addStretch()
        self.setLayout(layout)
        self.worker = GUIWorker(self.tasks)
        self.worker.progress_update.connect(self.pbar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.finished_signal.connect(self.close)
        self.worker.start()

    def center_window(self):
        qr = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        qr.moveCenter(screen)
        self.move(qr.topLeft())

def start_loader(tasks):
    app = QApplication.instance() or QApplication(sys.argv)
    loader = MaltegoGUILoader(tasks)
    loader.show()
    app.exec()

def run_terminal_loader(tasks):
    print('\n' + '=' * 50)
    print(' [!] BAYLAK OSINT SYSTEM - INITIALIZING ')
    print('=' * 50 + '\n')
    total = len(tasks)
    for i, task in enumerate(tasks):
        percent = int((i + 1) / total * 100)
        bar_length = 30
        filled_length = int(bar_length * (i + 1) // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r    Progress: |{bar}| {percent}% Processing: {task}')
        sys.stdout.flush()
        time.sleep(0.15)
    print(f'\n\n[+] Setup Complete. Launching Maltego Transform...\n')