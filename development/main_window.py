import sys, os
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QPushButton, QStackedWidget, QLayout, QSpacerItem, QWidget, QComboBox, QProgressBar, QLineEdit, QLayoutItem, QWidgetItem
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase, QColor, QPen
from pyqtgraph import PlotDataItem, PlotWidget
import serial.tools.list_ports
# from graph_canvas import GraphCanvas
import PyQt5.sip as sip
import config
import pandas as pd
from genose import AI_MODEL_DICT
import typing

WIDTH = 1280
HEIGHT = 720

WX = WIDTH / 100.0
HX = HEIGHT / 100.0

def px(x):
    return int(WX * x)

def py(x):
    return int(HX * x)

class CustomMainWindow(QMainWindow):
    resized = pyqtSignal()

    def __init__(self, parent = ..., flags = ...):
        super(CustomMainWindow, self).__init__()
    
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
    
class AutoFontContentButton(QPushButton):
    def __init__(self, text : str = "", font_idx : int = None, color_hex : str = "#FA6FC3", scale : float = 1.0, percentSize = QSize(20, 10), parent : CustomMainWindow | None = None):
        super().__init__(text, parent)

        self.__parent = parent

        self.color = color_hex
        self.percentSize = percentSize

        if(font_idx != None):
            button_font = QFont(QFontDatabase.applicationFontFamilies(font_idx)[0])
            new_font = button_font
            new_font.setPixelSize(50)
            new_font.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 120)

            self.setFont(new_font)

            self.setFontScale(scale)

        stylesheet = '''
            QPushButton {{
                border-radius : 10px; 
                background-color: {color}; 
                padding: 10px;
            }}
            QPushButton:pressed {{
                background-color: gray; 
            }}
            '''.format(color=self.color)

        self.setStyleSheet(stylesheet)

        effect = QGraphicsDropShadowEffect()

        effect.setBlurRadius(15)
        effect.setOffset(5, 5)

        self.setGraphicsEffect(effect)
        
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.setSizePolicy(sp)

        self.__parent.resized.connect(self.onResize)

        self.onResize()
    
    def onResize(self):
        self.setFixedSize(px(self.percentSize.width()), py(self.percentSize.height()))
    
    def setFontScale(self, scale):
        self.fontScale = scale

    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSize(py(self.fontScale))
        self.setFont(new_font)

        return super().resizeEvent(a0)
    
    def deleteLater(self):
        self.__parent.resized.disconnect(self.onResize)

        return super().deleteLater()

class AutoFontLineEdit(QLineEdit):
    def __init__(self, parent : CustomMainWindow | None = None, percentSize : QSize = QSize(5, 10)):
        super().__init__(parent)

        self.__parent = parent
        self.percentSize = percentSize
        
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        sp.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        self.setSizePolicy(sp)

        stylesheet = '''
                border-radius : 10px; 
                background-color : #D2D2D2;
                padding : 10px;
            '''
        self.setStyleSheet(stylesheet)

        self.__parent.resized.connect(self.onResize)

        self.onResize()

    def onResize(self):
        self.setFixedSize(px(self.percentSize.width()), py(self.percentSize.height()))

    def setPercentageSize(self, size : QSize):
        self.percentSize = size

    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSize(py(3))
        self.setFont(new_font)
        return super().resizeEvent(a0)
    
    def deleteLater(self):
        self.__parent.resized.disconnect(self.onResize)

        return super().deleteLater()
    
class MainWindow(CustomMainWindow):
    take_data_sig = pyqtSignal()
    model_select_sig = pyqtSignal(int)

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
        self.homeButton.setToolTip("Kembali ke beranda")
        self.resized.connect(lambda: self.homeButton.setGeometry(px(2), py(80), px(10), py(10)))

        self.aboutButton = ClickableLabel(self.appPage)
        self.aboutButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.aboutButton.setSourcePixmap(about_pixmap)
        self.aboutButton.clicked.connect(lambda: print("about"))
        self.aboutButton.setToolTip("Bantuan")
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
        self.changeContent("launch")
        self.currentScreen = "launch"

    def showHeader(self, text):
        self.header = self.createLabel(text, self.fonts[1], "#FA6FC3", self, QSize(20, 10))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        self.defaultButton = AutoFontContentButton(text="DEFAULT", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=3, parent=self)
        self.defaultButton.clicked.connect(lambda : self.changeContent("def-take-sample"))

        self.customButton = AutoFontContentButton(text="CUSTOM", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=3, parent=self)
        self.customButton.clicked.connect(lambda : self.changeContent("cus-genose-setting"))

        self.contentVbox.addWidget(self.defaultButton)
        self.contentVbox.addWidget(self.customButton)

    def hideHomeContent(self):
        # self.deleteContentButton(self.customButton)
        # self.deleteContentButton(self.defaultButton)
        self.defaultButton.deleteLater()
        self.customButton.deleteLater()

    def findPorts(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboxPortSelector.addItem(port.name)
    
    def showDefaultTakeSampleContent(self):
        self.currentScreen = "def-take-sample"
        self.takeDataButton = AutoFontContentButton(text="TAKE DATA SAMPLE", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=2, parent=self, percentSize=QSize(30, 10))
        # self.takeDataButton.clicked.connect(lambda : self.changeContent("def-model-selection"))
        self.takeDataButton.clicked.connect(lambda : self.take_data_sig.emit())

        self.comboxPortSelector = QComboBox()
        self.comboxPortSelector.setStyleSheet("QComboBox { margin:20; }")
        self.findPorts()

        self.showHeader("DEFAULT")

        self.contentVbox.addWidget(self.takeDataButton)
        self.contentVbox.addWidget(self.comboxPortSelector)

        self.spacer1 = QSpacerItem(10, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.spacer2 = QSpacerItem(10, 40, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.pbar = QProgressBar(self)
        sp = self.pbar.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.pbar.setSizePolicy(sp)
        self.pbar.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.pbar.setValue(0)

        self.barHbox = QHBoxLayout()

        self.barHbox.addItem(self.spacer1)
        self.barHbox.addWidget(self.pbar)
        self.barHbox.addItem(self.spacer2)

        self.contentVbox.addLayout(self.barHbox)

    def hideDefaultTakeSampleContent(self):
        self.barHbox.removeItem(self.spacer1)
        self.barHbox.removeItem(self.spacer2)
        self.takeDataButton.deleteLater()
        self.comboxPortSelector.deleteLater()
        self.pbar.deleteLater()
        self.barHbox.deleteLater()

    def showDefaultModelSelectionContent(self):
        self.currentScreen = "def-model-selection"
        self.svmButton = AutoFontContentButton("SVM", self.fonts[1], "#FA6FC3", 2, self, QSize(25, 10))
        self.svmButton.clicked.connect(lambda : self.model_select_sig.emit(AI_MODEL_DICT["SVM"]))

        self.rfButton = AutoFontContentButton("RANDOM FOREST", self.fonts[1], "#FA6FC3", 2, self, QSize(25, 10))
        self.rfButton.clicked.connect(lambda : self.model_select_sig.emit(AI_MODEL_DICT["RF"]))

        self.nnButton = AutoFontContentButton("NN", self.fonts[1], "#FA6FC3", 2, self, QSize(25, 10))
        self.nnButton.clicked.connect(lambda : self.model_select_sig.emit(AI_MODEL_DICT["NN"]))

        self.contentVbox.addWidget(self.svmButton)
        self.contentVbox.addWidget(self.rfButton)
        self.contentVbox.addWidget(self.nnButton)

    def hideDefaultModelSelectionContent(self):
        self.svmButton.deleteLater()
        self.rfButton.deleteLater()
        self.nnButton.deleteLater()

    def showDefaultPredictionResultContent(self):
        self.currentScreen = "def-prediction-result"
        
        self.sensorGraph = PlotWidget(self.appPage)
        
        self.contentVbox.addWidget(self.sensorGraph)

        self.showFooter("PREDICTION RESULT")
    
    def hideDefaultPredictionResultContent(self):
        self.sensorGraph.deleteLater()
        self.hideFooter()

    def showCustomGenoseSettingContent(self):
        self.currentScreen = "cus-genose-setting"
        
        self.showHeader("CUSTOM")
        
        self.inhaleLabel = self.createLabel("Inhale Timer (s)", self.fonts[1], "#D9D9D9", self.appPage, QSize(23, 8))
        self.flushLabel = self.createLabel("Flush Timer (s)", self.fonts[1], "#D9D9D9", self.appPage, QSize(23, 8))

        self.applyButton = AutoFontContentButton("apply", self.fonts[1], "#FA6FC3", 1.0, QSize(10, 6), self)
        self.inhaleValEdit = AutoFontLineEdit(self, QSize(5,8))
        self.flushValEdit = AutoFontLineEdit(self, QSize(5,8))

        self.labelVbox = QVBoxLayout()
        self.labelVbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelVbox.addWidget(self.inhaleLabel)
        self.labelVbox.addWidget(self.flushLabel)

        self.valueVbox = QVBoxLayout()
        self.valueVbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.valueVbox.addWidget(self.inhaleValEdit)
        self.valueVbox.addWidget(self.flushValEdit)

        self.settingHbox = QHBoxLayout()
        self.settingHbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.settingHbox.addLayout(self.labelVbox)
        self.settingHbox.addLayout(self.valueVbox)

        self.applyVbox = QVBoxLayout()
        self.applyVbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.applyVbox.addWidget(self.applyButton)

        self.contentVbox.addLayout(self.settingHbox)
        self.contentVbox.addLayout(self.applyVbox)

    def hideCustomGenoseSettingContent(self):
        self.clearContentVbox()

    def showCustomTakeDatasetContent(self):
        pass

    def hideCustomTakeDatasetContent(self):
        pass

    def showCustomPreprocessingContent(self):
        pass

    def hideCustomPreprocessingContent(self):
        pass

    def showCustomFeatureSelectContent(self):
        pass

    def hideCustomFeatureSelectContent(self):
        pass

    def showCustomAIModelContent(self):
        pass

    def hideCustomAIModelContent(self):
        pass

    def plot_sensor_data(self, sensor_datas : pd.DataFrame):
        sensor_colors = {
            'TGS2600'   : QColor(255, 255, 255, 127), 
            'TGS2602'   : QColor(255, 255, 0, 127), 
            'TGS816'    : QColor(0, 0, 255, 127), 
            'TGS813'    : QColor(255, 0, 0, 127), 
            'MQ8'       : QColor(255, 255, 255, 127),
            'TGS2611'   : QColor(255, 255, 0, 127), 
            'TGS2620'   : QColor(0, 0, 255, 127), 
            'TGS822'    : QColor(0, 255, 0, 127), 
            'MQ135'     : QColor(0, 255, 255, 127), 
            'MQ3'       : QColor(105, 100, 140, 127)
        }

        self.sensorGraph.plotItem.clear()

        for sensor_key in sensor_colors.keys():
            sensor_data = sensor_datas[sensor_key].to_list()

            pen = QPen()
            pen.setWidthF(0.5)
            pen.setColor(sensor_colors[sensor_key])
            
            self.sensorGraph.plotItem.addItem(
                PlotDataItem(
                    y=sensor_data, 
                    pen=pen
                )
            )

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
        elif(cur == "cus-genose-setting"):
            self.hideCustomGenoseSettingContent()

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
        elif(dest == "cus-genose-setting"):
            self.showCustomGenoseSettingContent()

    def deleteChilds(self, obj):
        if issubclass(obj.__class__, QLayout):
            for i in reversed(range(obj.count())):
                child = obj.itemAt(i)
                print(f"child ke {i} : {child}")

                self.deleteChilds(child)
                
                layout = obj.layout()
                layout.deleteLater()
        elif issubclass(obj.__class__, QWidgetItem):
            print("delete this")
            
            widget = obj.widget()
            widget.deleteLater()

        return True

    def clearContentVbox(self):
        for child in self.contentVbox.children():
            self.deleteChilds(child)

    def loadFonts(self):
        font1 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-Thin.ttf') 
        font2 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-ExtraBold.ttf') 
        font3 = QFontDatabase.addApplicationFont(f'{config.WORKING_DIR_PATH}/resources/Montserrat/static/Montserrat-SemiBold.ttf')

        self.fonts = [font1, font2, font3]

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
    
    # def createContentButton(self, text : str, font_idx : int, color_hex : str, scale : float, parent, minSize : QSize = QSize(20, 20)) -> AutoFontButton:
    #     button = self.createButton(text, font_idx, color_hex, scale, parent)

    #     sp = button.sizePolicy()
    #     sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
    #     button.setSizePolicy(sp)
        
    #     button.__onResize = lambda: button.setFixedSize(px(minSize.width()), py(minSize.height()))
    #     button.__onResize()

    #     self.resized.connect(button.__onResize)

    #     return button
    
    # def deleteContentButton(self, button : AutoFontButton):
    #     self.resized.disconnect(button.__onResize)
    #     button.deleteLater()
    
    def createLabel(self, text : str, font_idx : int, color_hex : str, parent, minSize : QSize = QSize(5, 5)) -> QLabel:
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

        label.__onResize = lambda: label.setFixedSize(px(minSize.width()), py(minSize.height()))
        label.__onResize()

        self.resized.connect(label.__onResize)

        return label
    
    def deleteLabel(self, label : AutoFontLabel):
        try:
            self.resized.disconnect(label.__onResize)
            label.deleteLater()
        except AttributeError as e:
            print("WARNING : ", e)
        except TypeError as e:
            print("WARNING : ", e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())