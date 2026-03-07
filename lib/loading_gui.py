import sys
import time
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QProgressBar, QLabel, QApplication, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor, QPixmap, QPainter, QTransform
from lib.styles.styles import COLORS

class RotatingLabel(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._angle = 0

    @pyqtProperty(float)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()

    def paintEvent(self, event):
        pix = self.pixmap()
        if not pix or pix.isNull():
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        cx = self.width() // 2
        cy = self.height() // 2
        painter.translate(cx, cy)
        painter.rotate(self._angle)
        painter.drawPixmap(-pix.width() // 2, -pix.height() // 2, pix)
        painter.end()

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
        total_tasks = len(self.tasks)
        for i, task in enumerate(self.tasks):
            self.status_update.emit(f'Loading: {task}...')
            sub_steps = 20
            for step in range(sub_steps):
                time.sleep(0.02)
                current_perc = int((i * sub_steps + step + 1) / (total_tasks * sub_steps) * 100)
                self.progress_update.emit(current_perc)
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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(480, 180)
        self.container = QWidget(self)
        self.container.setGeometry(10, 10, 460, 160)
        self.container.setStyleSheet(f"\n            QWidget {{ \n                background-color: {COLORS['bg_dark']}; \n                color: {COLORS['text_main']}; \n                border: 2px solid {COLORS['accent']}; \n                font-family: 'Segoe UI'; \n                border-radius: 15px; \n            }}\n        ")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.container.setGraphicsEffect(shadow)
        main_layout = QHBoxLayout(self.container)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(20)
        self.logo_label = RotatingLabel()
        base_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_path, 'styles', 'icons', 'logo.png')
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            self.logo_label.setPixmap(pixmap.scaled(70, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo_label.setText('LOGO')
            self.logo_label.setStyleSheet(f'color: {COLORS['accent']}; font-weight: bold; border: none;')
        self.logo_label.setFixedSize(80, 80)
        self.logo_label.setStyleSheet('border: none; background: transparent;')
        main_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self.animation = QPropertyAnimation(self.logo_label, b'angle')
        self.animation.setDuration(2000)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(360.0)
        self.animation.setLoopCount(-1)
        self.animation.start()
        content_layout = QVBoxLayout()
        self.title_label = QLabel('Maltego Transform Library')
        self.title_label.setStyleSheet(f'font-weight: bold; font-size: 16px; color: {COLORS['accent']}; border: none;')
        self.status_label = QLabel('Initializing Environment...')
        self.status_label.setStyleSheet(f'border: none; font-size: 11px; color: {COLORS['text_dim']};')
        self.pbar = QProgressBar()
        self.pbar.setMaximum(100)
        self.pbar.setTextVisible(False)
        self.pbar.setStyleSheet(f'\n            QProgressBar {{\n                border: 1px solid #333;\n                border-radius: 6px;\n                background-color: {COLORS['bg_card']};\n                height: 10px;\n            }}\n            QProgressBar::chunk {{\n                background-color: {COLORS['accent']};\n                border-radius: 4px;\n                margin: 1px;\n            }}\n        ')
        content_layout.addStretch()
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.status_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(self.pbar)
        content_layout.addStretch()
        main_layout.addLayout(content_layout)
        self.worker = GUIWorker(self.tasks)
        self.worker.progress_update.connect(self.pbar.setValue)
        self.worker.status_update.connect(self.status_label.setText)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def on_finished(self):
        if hasattr(self, 'animation'):
            self.animation.stop()
        self.worker.quit()
        self.worker.wait()
        self.close()

    def center_window(self):
        qr = self.frameGeometry()
        screen = self.screen().availableGeometry().center()
        qr.moveCenter(screen)
        self.move(qr.topLeft())

def start_gui_loader(tasks):
    app = QApplication.instance() or QApplication(sys.argv)
    loader = MaltegoGUILoader(tasks)
    loader.show()
    app.exec()