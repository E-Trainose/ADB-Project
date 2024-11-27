import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QSize, QMargins
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QLayout, QSpacerItem
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase

class ResizedLogoLabel(QLabel):
    def setSourcePixmap(self, source : QPixmap):
        self.sourcePixmap = source
    def resizeEvent(self, a0):
        size = self.size()
        
        if(self.sourcePixmap):
            logo_pixmap = self.sourcePixmap.scaled(
                size.height(), 
                size.width(),   
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
            )
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
    
class AutoFontButton(QPushButton):
    def setScalePoint(self, point):
        self.scalePoint = point

    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSizeF(a0.size().width() / self.scalePoint)
        self.setFont(new_font)
        return super().resizeEvent(a0)

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

        font1 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-Thin.ttf') 
        font2 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-ExtraBold.ttf') 
        font3 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-SemiBold.ttf')

        self.fonts = [font1, font2, font3]

        self.stackedWidget.setCurrentIndex(0)
        self.currentScreen = "launch"

        self.setupLaunchScreen()
        self.setupAppScreen()

    def setupLaunchScreen(self):
        self.startButton = self.createButton("START", self.fonts[1], "#FA6FC3", 12)
        self.startButton.clicked.connect(lambda : self.navToApp())
        self.startButtonVBox.addWidget(self.startButton)

    def navToApp(self):
        pages : QStackedWidget = self.stackedWidget
        pages.setCurrentIndex(1)
        
        self.changeContent("home")

    def setupAppScreen(self):
        logo_pixmap = QPixmap("development/resources/etrainose_logo.png")
        self.logoHeader = ResizedLogoLabel()
        self.logoHeader.setSourcePixmap(logo_pixmap)
        self.logoHeader.setMinimumSize(100, 100)

        self.homeButton = self.createButton("HOME", self.fonts[1], "#FA6FC3")
        self.infoButton = self.createButton("INFO", self.fonts[1], "#FA6FC3")

        layout = QHBoxLayout(self.widget_2)
        layout.addWidget(self.logoHeader)
        self.verticalSpacer = QSpacerItem(100, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addItem(self.verticalSpacer)

        layout = QHBoxLayout(self.widget)
        layout.addWidget(self.homeButton)
        self.verticalSpacer1 = QSpacerItem(100, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addItem(self.verticalSpacer1)

        layout = QHBoxLayout(self.widget_4)
        self.verticalSpacer2 = QSpacerItem(100, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        layout.addItem(self.verticalSpacer2)
        layout.addWidget(self.infoButton)

        self.contentLayout = QVBoxLayout(self.widget_3)

    def showHeader(self, text):
        self.header = self.createButton(text, self.fonts[1], "#FA6FC3")
        layout = QVBoxLayout(self.widget_5)
        layout.addWidget(self.header)

    def hideHeader(self, text):
        self.header.deleteLater()
    
    def showFooter(self, text):
        self.footer = self.createButton(text, self.fonts[1], "#FA6FC3")
        layout = QVBoxLayout(self.widget_7)
        layout.addWidget(self.footer)

    def hideFooter(self, text):
        self.footer.deleteLater()

    def showHomeContent(self):
        self.currentScreen = "home"

        self.selectDefaultButton = self.createButton("DEFAULT", self.fonts[1], "#537EFF", 15)
        self.selectCustomButton = self.createButton("CUSTOM", self.fonts[1], "#FA6FC3", 15)
        
        self.selectDefaultButton.clicked.connect(lambda : self.changeContent('def_take_sample'))

        self.contentLayout.addWidget(self.selectDefaultButton)
        self.contentLayout.addWidget(self.selectCustomButton)
    
    def hideHomeContent(self):
        self.selectDefaultButton.deleteLater()
        self.selectCustomButton.deleteLater()
    
    def showDefaultTakeSampleContent(self):
        self.takeDataSampleButton = self.createButton("TAKE DATA SAMPLE", self.fonts[1], "#537EFF", 30)

        self.contentLayout.addWidget(self.takeDataSampleButton)

        self.showHeader("DEFAULT")

    def hideDefaultTakeSampleContent(self):
        self.takeDataSampleButton.deleteLater()

    def changeContent(self, dest):
        cur = self.currentScreen

        #cleanup last content
        if(cur == "home"):
            self.hideHomeContent()    
        elif(cur == "def_take_sample"):
            self.hideDefaultTakeSampleContent()

        #show new content
        if(dest == "home"):
            self.showHomeContent()    
        elif(dest == "def_take_sample"):
            self.showDefaultTakeSampleContent()

    def resizeEvent(self, a0):
        w = a0.size().width()
        self.verticalSpacer.changeSize(int(w/5), 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.verticalSpacer1.changeSize(int(w/5), 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.verticalSpacer2.changeSize(int(w/5), 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        return super().resizeEvent(a0)

    def createButton(self, text : str, font_idx : int, color_hex : str, scale_point = 20.0) -> AutoFontButton:
        color = color_hex
        button_font = QFont(QFontDatabase.applicationFontFamilies(font_idx)[0])
        button = AutoFontButton(text, self)
        button.setScalePoint(scale_point)
        
        stylesheet = '''
            QPushButton {{
                border-radius : 10px; 
                background-color: {color}; 
                padding: 10px;
            }}
            QPushButton:pressed {{
                border-radius : 10px; 
                background-color: gray; 
                padding: 10px;
            }}
            '''.format(color=color)

        button.setStyleSheet(stylesheet)

        new_font = button_font
        new_font.setPixelSize(50)
        new_font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 120)

        button.setFont(new_font)
        
        effect = QGraphicsDropShadowEffect()

        effect.setBlurRadius(15)
        effect.setOffset(5, 5)

        button.setGraphicsEffect(effect)

        return button

# Main execution
if __name__ == '__main__':
    app = QApplication(sys.argv)    
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
