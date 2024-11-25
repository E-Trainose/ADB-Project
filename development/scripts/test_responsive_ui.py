import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QLabel, QAbstractButton
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent

class ResizedLogoLabel(QLabel):
    def setSourcePixmap(self, source : QPixmap):
        self.sourcePixmap = source

    def resizeEvent(self, a0):
        size = self.size()
        
        if(self.sourcePixmap):
            logo_pixmap = self.sourcePixmap.scaled(size.height(), size.width(),   aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio)
            self.setPixmap(logo_pixmap)

        return super().resizeEvent(a0)

class PicButton(QAbstractButton):
    def __init__(self, normal_pixmap : QPixmap, down_pixmap : QPixmap, parent=None):
        super(PicButton, self).__init__(parent)
        self.normal_pixmap = normal_pixmap
        self.down_pixmap = down_pixmap

    def paintEvent(self, e : QPaintEvent):
        use_pixmap = None

        if(self.isDown()):
            use_pixmap = self.down_pixmap
        else:
            use_pixmap = self.normal_pixmap

        pxsize = use_pixmap.size()
        rect = e.rect()

        dh = rect.height() / pxsize.height()
        dw = rect.width() / pxsize.width()

        print(dh, dw)

        scale = min([dh, dw])

        pxsize = QSize(int(pxsize.width() * scale ), int(pxsize.height() * scale))

        slw = int( (rect.size().width() - pxsize.width()) / 2 )
        
        rect.setLeft(slw)
        rect.setSize(pxsize)

        painter = QPainter(self)
        painter.drawPixmap(rect, use_pixmap)
    
    def resizeEvent(self, a0):
        return super().resizeEvent(a0)
    
    def sizeHint(self):
        return self.normal_pixmap.size()
    
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Load the .ui file dynamically
        uic.loadUi('development/responsive.ui', self)

        self.logoLabel = ResizedLogoLabel()

        graph_layout = QVBoxLayout(self.logoWidget)
        graph_layout.addWidget(self.logoLabel)

        logo_pixmap = QPixmap("development/resources/etrainose_logo.png")
        self.logoLabel.setSourcePixmap(logo_pixmap)

        start_btn_pixmap = QPixmap("development/resources/start_button.png")
        start_btn_down_pixmap = QPixmap("development/resources/start_button_down.png")

        self.startButton = PicButton(normal_pixmap=start_btn_pixmap, down_pixmap=start_btn_down_pixmap)
        self.verticalLayout_4.addWidget(self.startButton)

# Main execution
if __name__ == '__main__':
    app = QApplication(sys.argv)    
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
