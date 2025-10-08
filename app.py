import sys
import Quartz
import AppKit
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QMessageBox, QGraphicsDropShadowEffect, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class KeyboardBlockerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.blocking = False
        self.event_tap = None
        self.run_loop_thread = None
        self.runloop = None

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Keyboard Cleaner")
        self.setFixedSize(400, 600)

        # Main widget
        main_widget = QWidget()
        main_widget.setStyleSheet("background-color: #1a1a1a;")
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(0)

        # Title
        title = QLabel("Keyboard Cleaner")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("SF Pro Display", 24, QFont.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(title)

        layout.addSpacing(60)

        # Status Circle
        self.status_circle = QLabel("✓")
        self.status_circle.setAlignment(Qt.AlignCenter)
        self.status_circle.setFixedSize(140, 140)
        self.status_circle.setFont(QFont("SF Pro Display", 70, QFont.Bold))
        self.status_circle.setStyleSheet("""
            background-color: #10b981;
            color: white;
            border-radius: 70px;
        """)

        circle_shadow = QGraphicsDropShadowEffect()
        circle_shadow.setBlurRadius(30)
        circle_shadow.setColor(QColor(16, 185, 129, 120))
        circle_shadow.setOffset(0, 6)
        self.status_circle.setGraphicsEffect(circle_shadow)

        layout.addWidget(self.status_circle, alignment=Qt.AlignCenter)

        layout.addSpacing(30)

        # Status Text
        self.status_text = QLabel("Keyboard Active")
        self.status_text.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        self.status_text.setStyleSheet("color: #10b981; background: transparent;")
        self.status_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_text)

        layout.addSpacing(10)

        self.status_subtitle = QLabel("Ready to clean")
        self.status_subtitle.setFont(QFont("SF Pro Display", 14))
        self.status_subtitle.setStyleSheet("color: #666; background: transparent;")
        self.status_subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_subtitle)

        layout.addSpacing(60)

        # Lock Button
        self.lock_btn = QPushButton("Lock Keyboard")
        self.lock_btn.setFont(QFont("SF Pro Display", 15, QFont.Bold))
        self.lock_btn.setFixedHeight(55)
        self.lock_btn.setCursor(Qt.PointingHandCursor)
        self.lock_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #b91c1c;
            }
            QPushButton:disabled {
                background-color: #374151;
                color: #6b7280;
            }
        """)

        lock_shadow = QGraphicsDropShadowEffect()
        lock_shadow.setBlurRadius(20)
        lock_shadow.setColor(QColor(220, 38, 38, 100))
        lock_shadow.setOffset(0, 4)
        self.lock_btn.setGraphicsEffect(lock_shadow)

        self.lock_btn.clicked.connect(self.lock_keyboard)
        layout.addWidget(self.lock_btn)

        layout.addSpacing(15)

        # Unlock Button
        self.unlock_btn = QPushButton("Unlock Keyboard")
        self.unlock_btn.setFont(QFont("SF Pro Display", 15, QFont.Bold))
        self.unlock_btn.setFixedHeight(55)
        self.unlock_btn.setCursor(Qt.PointingHandCursor)
        self.unlock_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)

        unlock_shadow = QGraphicsDropShadowEffect()
        unlock_shadow.setBlurRadius(20)
        unlock_shadow.setColor(QColor(16, 185, 129, 100))
        unlock_shadow.setOffset(0, 4)
        self.unlock_btn.setGraphicsEffect(unlock_shadow)

        self.unlock_btn.clicked.connect(self.unlock_keyboard)
        layout.addWidget(self.unlock_btn)

        layout.addStretch()

    # ---------- Quartz Event Tap ----------
    def event_callback(self, proxy, type_, event, refcon):
        if self.blocking:
            return None
        return event

    def run_loop(self, run_loop_source):
        try:
            self.runloop = Quartz.CFRunLoopGetCurrent()
            Quartz.CFRunLoopAddSource(self.runloop, run_loop_source, Quartz.kCFRunLoopCommonModes)
            Quartz.CGEventTapEnable(self.event_tap, True)
            Quartz.CFRunLoopRun()
        except Exception as e:
            print(f"[RunLoop Error] {e}")
        finally:
            print("Run loop incheiat")

    def stop_run_loop(self):
        if self.runloop:
            Quartz.CFRunLoopStop(self.runloop)
            self.runloop = None

    # ---------- UI Logic ----------
    def lock_keyboard(self):
        if self.blocking:
            QMessageBox.warning(self, "Already Locked", "Keyboard is already locked!")
            return

        self.blocking = True

        # Update UI - RED
        self.status_circle.setText("🔒")
        self.status_circle.setStyleSheet("""
            background-color: #dc2626;
            color: white;
            border-radius: 70px;
        """)

        circle_shadow = QGraphicsDropShadowEffect()
        circle_shadow.setBlurRadius(30)
        circle_shadow.setColor(QColor(220, 38, 38, 120))
        circle_shadow.setOffset(0, 6)
        self.status_circle.setGraphicsEffect(circle_shadow)

        self.status_text.setText("Keyboard Locked")
        self.status_text.setStyleSheet("color: #dc2626; background: transparent;")
        self.status_subtitle.setText("Safe to clean")
        self.lock_btn.setEnabled(False)

        # Create event tap
        self.event_tap = Quartz.CGEventTapCreate(
            Quartz.kCGSessionEventTap,
            Quartz.kCGHeadInsertEventTap,
            Quartz.kCGEventTapOptionDefault,
            Quartz.CGEventMaskBit(Quartz.kCGEventKeyDown)
            | Quartz.CGEventMaskBit(Quartz.kCGEventFlagsChanged)
            | Quartz.CGEventMaskBit(Quartz.kCGEventKeyUp),
            self.event_callback,
            None
        )

        if not self.event_tap:
            QMessageBox.critical(
                self,
                "Permission Error",
                "Nu pot bloca tastatura.\nAcorda permisiune in: System Settings > Privacy & Security > Accessibility.",
            )
            self.blocking = False
            self._reset_ui()
            return

        run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self.event_tap, 0)
        self.run_loop_thread = threading.Thread(target=self.run_loop, args=(run_loop_source,), daemon=True)
        self.run_loop_thread.start()

        QMessageBox.information(self, "Keyboard Locked", "Tastatura este blocata.\nPoti curata in siguranta!")

    def unlock_keyboard(self):
        if not self.blocking:
            QMessageBox.information(self, "Already Unlocked", "Keyboard is already unlocked!")
            return

        self.blocking = False
        print("Deblocare tastatura...")

        if self.event_tap:
            Quartz.CGEventTapEnable(self.event_tap, False)
            self.event_tap = None
        self.stop_run_loop()

        self._reset_ui()
        QMessageBox.information(self, "Keyboard Unlocked", "Tastatura este activa din nou.")

    def _reset_ui(self):
        """Reset to GREEN"""
        self.status_circle.setText("✓")
        self.status_circle.setStyleSheet("""
            background-color: #10b981;
            color: white;
            border-radius: 70px;
        """)

        circle_shadow = QGraphicsDropShadowEffect()
        circle_shadow.setBlurRadius(30)
        circle_shadow.setColor(QColor(16, 185, 129, 120))
        circle_shadow.setOffset(0, 6)
        self.status_circle.setGraphicsEffect(circle_shadow)

        self.status_text.setText("Keyboard Active")
        self.status_text.setStyleSheet("color: #10b981; background: transparent;")
        self.status_subtitle.setText("Ready to clean")
        self.lock_btn.setEnabled(True)

    def closeEvent(self, event):
        self.blocking = False
        if self.event_tap:
            Quartz.CGEventTapEnable(self.event_tap, False)
        self.stop_run_loop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeyboardBlockerApp()
    window.show()
    sys.exit(app.exec_())