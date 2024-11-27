import sys
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QLayout, QSpacerItem, QWidget
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase

WIDTH = 1280
HEIGHT = 720

WX = WIDTH / 100.0
HX = HEIGHT / 100.0

def px(x):
    return int(WX * x)

def py(x):
    return int(HX * x)

class ResizedLogoLabel(QLabel):
    def setSourcePixmap(self, source : QPixmap):
        self.sourcePixmap = source
    def resizeEvent(self, a0):
        size = self.geometry()
        
        if(self.sourcePixmap):
            logo_pixmap = self.sourcePixmap.scaled(
                int(size.height() * 0.9),
                int(size.width() * 0.9), 
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
            )
            self.setPixmap(logo_pixmap)

        return super().resizeEvent(a0)
    
class ClickableLabel(ResizedLogoLabel):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        super(ClickableLabel, self).mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
    
class AutoFontButton(QPushButton):
    def resizeEvent(self, a0):
        new_font = self.font()
        # new_font.setPointSizeF(a0.size().width() / 30.0)
        new_font.setPointSize(py(3))
        self.setFont(new_font)

        return super().resizeEvent(a0)

class MainWindow(QMainWindow):
    resized = pyqtSignal()

    def __init__(self, parent = ..., flags = ...):
        super(MainWindow, self).__init__()

        self.currentScreen = "launch"

        self.setStyleSheet("MainWindow { background-color : #537EFF; }")
        self.resize(WIDTH, HEIGHT)

        self.pages = QStackedWidget(self)
        self.pages.setStyleSheet("QStackedWidget { background-color : white; border : 20 solid #537EFF; border-radius: 30; }")

        self.launchPage = QWidget()
        self.appPage = QWidget()

        self.pages.addWidget(self.launchPage)
        self.pages.addWidget(self.appPage)
        self.resized.connect(lambda: self.pages.setGeometry(px(0), py(0), px(100), py(100)))

        self.loadFonts()

        self.startButton = self.createButton("START", self.fonts[1], "#FA6FC3", self.launchPage)
        self.startButton.clicked.connect(lambda : self.goToApp())
        self.resized.connect(lambda: self.startButton.setGeometry(px(40), py(80), px(20), py(10)))

        logo_pixmap = QPixmap("development/resources/etrainose_logo.png")
        home_pixmap = QPixmap("development/resources/home_icon.png")
        about_pixmap = QPixmap("development/resources/about_icon.png")

        self.launchLogo = ResizedLogoLabel(self.launchPage)
        self.launchLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.launchLogo.setSourcePixmap(logo_pixmap)
        self.resized.connect(lambda: self.launchLogo.setGeometry(px(30), py(10), px(40), py(60)))

        self.appLogo = ResizedLogoLabel(self.appPage)
        self.appLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.appLogo.setSourcePixmap(logo_pixmap)
        self.resized.connect(lambda: self.appLogo.setGeometry(px(2), py(2), px(10), py(20)))

        self.homeButton = ClickableLabel(self.appPage)
        self.homeButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.homeButton.setSourcePixmap(home_pixmap)
        # self.homeButton.clicked.connect(lambda: self.goToHome())
        self.resized.connect(lambda: self.homeButton.setGeometry(px(2), py(80), px(10), py(10)))

        self.aboutButton = ClickableLabel(self.appPage)
        self.aboutButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.aboutButton.setSourcePixmap(about_pixmap)
        self.aboutButton.clicked.connect(lambda: print("about"))
        self.resized.connect(lambda: self.aboutButton.setGeometry(px(86), py(2), px(10), py(10)))

        self.widget = QWidget(self.appPage)
        self.widget.setStyleSheet("background-color:blue;")
        self.resized.connect(lambda: self.widget.setGeometry(QRect(px(20), py(20), px(60), py(60))))
        self.vbox = QVBoxLayout(self.widget)
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def goToApp(self):
        self.pages.setCurrentIndex(1)
        self.showHomeContent()

    # def goToHome(self):
    #     pass

    def showHomeContent(self):
        self.currentScreen = "home"
        self.defaultButton = self.createButton("DEFAULT", self.fonts[1], "#FA6FC3", self.appPage)
        self.defaultButton.clicked.connect(lambda : self.changeContent("def-take-sample"))

        sp = self.defaultButton.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.defaultButton.setSizePolicy(sp)
        
        self.defaultButton.setMinimumSize(px(20), py(20))
        self.defaultButton.__onResize = lambda: self.defaultButton.setMinimumSize(px(20), py(20))
        self.resized.connect(self.defaultButton.__onResize)
        
        self.vbox.addWidget(self.defaultButton)

    def hideHomeContent(self):
        self.resized.disconnect(self.defaultButton.__onResize)
        self.defaultButton.deleteLater()
    
    def showDefaultTakeSampleContent(self):
        self.currentScreen = "def-take-sample"
        self.takeDataButton = self.createButton("TAKE DATA SAMPLE", self.fonts[1], "#FA6FC3", self.appPage)
        self.takeDataButton.clicked.connect(lambda : print("hello"))

        # sp = self.takeDataButton.sizePolicy()
        # sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        # self.takeDataButton.setSizePolicy(sp)
        
        # self.takeDataButton.setMinimumSize(px(40), py(20))
        # self.resized.connect(lambda: self.takeDataButton.setMinimumSize(px(40), py(20)))

        self.vbox.addWidget(self.takeDataButton)

    def hideDefaultTakeSampleContent(self):
        self.takeDataButton.deleteLater()

    def changeContent(self, dest):
        cur = self.currentScreen

        #cleanup last content
        if(cur == "home"):
            self.hideHomeContent()    
        elif(cur == "def-take-sample"):
            self.hideDefaultTakeSampleContent()

        #show new content
        if(dest == "home"):
            self.showHomeContent()
        elif(dest == "def-take-sample"):
            self.showDefaultTakeSampleContent()

    def loadFonts(self):
        font1 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-Thin.ttf') 
        font2 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-ExtraBold.ttf') 
        font3 = QFontDatabase.addApplicationFont('development/resources/Montserrat/static/Montserrat-SemiBold.ttf')

        self.fonts = [font1, font2, font3]

    def updateGeometries(self, a0):
        global WIDTH, HEIGHT, WX, HX
        
        WIDTH = a0.size().width()
        HEIGHT = a0.size().height()
        WX = WIDTH / 100.0
        HX = HEIGHT / 100.0

        self.resized.emit()

    def resizeEvent(self, a0):
        self.updateGeometries(a0)

        return super().resizeEvent(a0)
    
    def createButton(self, text : str, font_idx : int, color_hex : str, parent) -> AutoFontButton:
        color = color_hex
        button_font = QFont(QFontDatabase.applicationFontFamilies(font_idx)[0])
        button = AutoFontButton(text, parent)
        
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())