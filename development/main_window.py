import sys, os
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QLayout, QSpacerItem, QWidget, QComboBox
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase
import serial.tools.list_ports
from graph_canvas import GraphCanvas
import PyQt5.sip as sip
import config

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
    def setFontScale(self, scale):
        self.fontScale = scale

    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSize(py(self.fontScale))
        self.setFont(new_font)

        return super().resizeEvent(a0)
    
class AutoFontLabel(QLabel):
    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSize(py(3))
        self.setFont(new_font)
        return super().resizeEvent(a0)

class MainWindow(QMainWindow):
    resized = pyqtSignal()
    take_data_sig = pyqtSignal()
    model_select_sig = pyqtSignal(str)

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

        self.startButton = self.createButton("START", self.fonts[1], "#FA6FC3", 3, self.launchPage)
        self.startButton.clicked.connect(lambda : self.goToApp())
        self.resized.connect(lambda: self.startButton.setGeometry(px(40), py(80), px(20), py(10)))

        logo_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/etrainose_logo.png")
        home_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/home_icon.png")
        about_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/about_icon.png")

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
        self.homeButton.clicked.connect(lambda: self.goToLaunch())
        self.resized.connect(lambda: self.homeButton.setGeometry(px(2), py(80), px(10), py(10)))

        self.aboutButton = ClickableLabel(self.appPage)
        self.aboutButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.aboutButton.setSourcePixmap(about_pixmap)
        self.aboutButton.clicked.connect(lambda: print("about"))
        self.resized.connect(lambda: self.aboutButton.setGeometry(px(86), py(2), px(10), py(10)))

        self.headerWidget = QWidget(self.appPage)
        # self.headerWidget.setStyleSheet("background-color:red;")
        self.resized.connect(lambda: self.headerWidget.setGeometry(QRect(px(20), py(4), px(60), py(14))))
        self.headerVbox = QVBoxLayout(self.headerWidget)
        self.headerVbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.footerWidget = QWidget(self.appPage)
        # self.footerWidget.setStyleSheet("background-color:green;")
        self.resized.connect(lambda: self.footerWidget.setGeometry(QRect(px(20), py(80), px(60), py(14))))
        self.footerVbox = QVBoxLayout(self.footerWidget)
        self.footerVbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.contentWidget = QWidget(self.appPage)
        # self.contentWidget.setStyleSheet("background-color:blue;")
        self.resized.connect(lambda: self.contentWidget.setGeometry(QRect(px(20), py(18.5), px(60), py(60))))
        self.contentVbox = QVBoxLayout(self.contentWidget)
        self.contentVbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def goToApp(self):
        self.pages.setCurrentIndex(1)
        self.changeContent("home")

    def goToLaunch(self):
        self.pages.setCurrentIndex(0)
        self.changeContent("home")
        self.currentScreen = "launch"

    def showHeader(self, text):
        self.header = self.createLabel(text, self.fonts[1], "#FA6FC3", self)

        self.headerVbox.addWidget(self.header)

    def hideHeader(self):
        try:
            self.deleteLabel(self.header)
        except AttributeError as e:
            print(e)
    
    def showFooter(self, text):
        self.footer = self.createLabel(text, self.fonts[1], "#FA6FC3", self)
        
        self.footerVbox.addWidget(self.footer)

    def hideFooter(self):
        try:
            self.deleteLabel(self.footer)
        except AttributeError as e:
            print(e)

    def showHomeContent(self):
        self.currentScreen = "home"
        self.defaultButton = self.createContentButton("DEFAULT", self.fonts[1], "#FA6FC3", 3, self.appPage)
        self.defaultButton.clicked.connect(lambda : self.changeContent("def-take-sample"))

        self.contentVbox.addWidget(self.defaultButton)

    def hideHomeContent(self):
        self.deleteContentButton(self.defaultButton)

    def findPorts(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboxPortSelector.addItem(port.name)
    
    def showDefaultTakeSampleContent(self):
        self.currentScreen = "def-take-sample"
        self.takeDataButton = self.createContentButton("TAKE DATA SAMPLE", self.fonts[1], "#FA6FC3", 2, self.appPage, QSize(30, 10))
        self.takeDataButton.clicked.connect(lambda : self.changeContent("def-model-selection"))
        # self.takeDataButton.clicked.connect(lambda : self.take_data_sig.emit())

        self.comboxPortSelector = QComboBox()
        self.comboxPortSelector.setStyleSheet("QComboBox { margin:20; }")
        self.findPorts()

        self.showHeader("DEFAULT")

        self.contentVbox.addWidget(self.takeDataButton)
        self.contentVbox.addWidget(self.comboxPortSelector)

    def hideDefaultTakeSampleContent(self):
        self.deleteContentButton(self.takeDataButton)
        self.comboxPortSelector.deleteLater()

    def showDefaultModelSelectionContent(self):
        self.currentScreen = "def-model-selection"
        self.svmButton = self.createContentButton("SVM", self.fonts[1], "#FA6FC3", 2, self.appPage, QSize(25, 10))
        self.svmButton.clicked.connect(lambda : self.changeContent("def-prediction-result"))
        # self.svmButton.clicked.connect(lambda : self.model_select_sig.emit("svm"))

        self.rfButton = self.createContentButton("RANDOM FOREST", self.fonts[1], "#FA6FC3", 2, self.appPage, QSize(25, 10))
        self.rfButton.clicked.connect(lambda : self.model_select_sig.emit("rf"))

        self.nnButton = self.createContentButton("NN", self.fonts[1], "#FA6FC3", 2, self.appPage, QSize(25, 10))
        self.nnButton.clicked.connect(lambda : self.model_select_sig.emit("nn"))

        self.contentVbox.addWidget(self.svmButton)
        self.contentVbox.addWidget(self.rfButton)
        self.contentVbox.addWidget(self.nnButton)

    def hideDefaultModelSelectionContent(self):
        self.deleteContentButton(self.svmButton)
        self.deleteContentButton(self.rfButton)
        self.deleteContentButton(self.nnButton)

    def showDefaultPredictionResultContent(self):
        self.currentScreen = "def-prediction-result"
        # self.resultLabel = self.createLabel("PREDICTION RESULT", self.fonts[1], "gray", self.appPage)
        self.graph_canvas = GraphCanvas(self.appPage)
        self.graph_canvas.update_plot_([0,1,2,3,4,5])
        # self.graph_canvas.resize()

        self.contentVbox.addWidget(self.graph_canvas)

        self.showFooter("PREDICTION RESULT")
    
    def hideDefaultPredictionResultContent(self):
        print("deleted")
        self.graph_canvas.deleteLater()
        self.hideFooter()
        # self.deleteLabel(self.resultLabel)

    def changeContent(self, dest):
        cur = self.currentScreen

        #cleanup last content
        if(cur == "home"):
            self.hideHomeContent()
        elif(cur == "def-take-sample"):
            self.hideDefaultTakeSampleContent()
        elif(cur == "def-model-selection"):
            self.hideDefaultModelSelectionContent()
        elif(cur == "def-prediction-result"):
            self.hideDefaultPredictionResultContent()

        #show new content
        if(dest == "home"):
            self.showHomeContent()

            self.hideHeader()
            self.hideFooter()

        elif(dest == "def-take-sample"):
            self.showDefaultTakeSampleContent()
        elif(dest == "def-model-selection"):
            self.showDefaultModelSelectionContent()
        elif(dest == "def-prediction-result"):
            self.showDefaultPredictionResultContent()

    def loadFonts(self):
        print(os.path.dirname(__file__) )
        font1 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-Thin.ttf') 
        font2 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-ExtraBold.ttf') 
        font3 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-SemiBold.ttf')

        print(font1)
        self.fonts = [font1, font2, font3]
        
        print(QFontDatabase.applicationFontFamilies(font1))

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
    
    def createButton(self, text : str, font_idx : int, color_hex : str, scale : float, parent) -> AutoFontButton:
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

        button.setFontScale(scale)

        effect = QGraphicsDropShadowEffect()

        effect.setBlurRadius(15)
        effect.setOffset(5, 5)

        button.setGraphicsEffect(effect)
        
        return button
    
    def createContentButton(self, text : str, font_idx : int, color_hex : str, scale : float, parent, minSize : QSize = QSize(20, 20)) -> AutoFontButton:
        button = self.createButton(text, font_idx, color_hex, scale, parent)

        sp = button.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        button.setSizePolicy(sp)
        
        button.__onResize = lambda: button.setFixedSize(px(minSize.width()), py(minSize.height()))
        button.__onResize()

        self.resized.connect(button.__onResize)

        return button
    
    def deleteContentButton(self, button : AutoFontButton):
        self.resized.disconnect(button.__onResize)
        button.deleteLater()
    
    def createLabel(self, text : str, font_idx : int, color_hex : str, parent) -> QLabel:
        color = color_hex
        font = QFont(QFontDatabase.applicationFontFamilies(font_idx)[0])
        label = AutoFontLabel(text, parent)

        stylesheet = '''
            QLabel {{
                border-radius : 10px; 
                background-color: {color}; 
                padding: 10px;
            }}
            '''.format(color=color)
        
        label.setStyleSheet(stylesheet)
        label.setFont(font)

        # responsive settings
        sp = label.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        label.setSizePolicy(sp)

        label.__onResize = lambda: label.setMinimumSize(px(5), py(5))
        label.__onResize()

        self.resized.connect(label.__onResize)

        return label
    
    def deleteLabel(self, label : AutoFontLabel):
        try:
            self.resized.disconnect(label.__onResize)
            label.deleteLater()
        except AttributeError as e:
            print("WARNING : ", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())