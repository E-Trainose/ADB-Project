import sys, os
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect, QPropertyAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidgetItem, QGraphicsOpacityEffect
from PyQt5.QtWidgets import QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QLineEdit, QLayoutItem, QFrame
from PyQt5.QtWidgets import QPushButton, QStackedWidget, QLayout, QSpacerItem, QWidget, QComboBox, QProgressBar
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase, QColor, QPen
from pyqtgraph import PlotDataItem, PlotWidget

WIDTH = 1280
HEIGHT = 720

Wx = WIDTH / 4

snapGridW = [Wx * 1, Wx * 2, Wx * 3, Wx * 4]
snapGridWV = [0, Wx * 1, Wx * 2, Wx * 3]

class DraggableWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.mousePressPos = None
        self.mouseMovePos = None

        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Policy.Fixed)

        self.setSizePolicy(sp)

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.setStyleSheet("""
            DraggableWidget { 
                border: 5px solid black;                           
            }                         
        """)

    def focusInEvent(self, a0):
        self.setStyleSheet("""
            DraggableWidget { 
                border: 5px solid red;
            }                         
        """)
        return super().focusInEvent(a0)
    
    def focusOutEvent(self, a0):
        self.setStyleSheet("""
            DraggableWidget { 
                border: 5px solid black;
            }                         
        """)
        return super().focusOutEvent(a0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePressPos = event.globalPos()
            self.mouseMovePos = event.globalPos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.mousePressPos:
                delta = event.globalPos() - self.mouseMovePos
                self.move(self.x() + delta.x(), self.y() + delta.y())
                self.mouseMovePos = event.globalPos()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.globalPos()
            print(pos)

            for i in range(0, len(snapGridW)):
                if(self.x() < snapGridW[i]):
                    self.move(int(snapGridWV[i]), int(100))
                    break

            self.mousePressPos = None

        super().mouseReleaseEvent(event)

class AppWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.resize(WIDTH, HEIGHT)

        self.drag_label1 = DraggableWidget(self)
        self.drag_label1.setGeometry(400, 100, 300, 200)
        
        self.drag_label = DraggableWidget(self)
        self.drag_label.setGeometry(100, 100, 300, 450)

        self.drag_vbox = QVBoxLayout(self.drag_label)
        self.drag_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("test")

        sp = self.label.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)

        self.label.setSizePolicy(sp)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("background-color: green;")

        self.drag_vbox.addWidget(self.label)

        self.button = QPushButton("apply", self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AppWindow()
    main_win.show()
    sys.exit(app.exec_())