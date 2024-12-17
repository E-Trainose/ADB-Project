import sys, os
from PyQt5.QtCore import Qt, QSize, QMargins, pyqtSignal, QRect, QPropertyAnimation, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidgetItem, QGraphicsOpacityEffect
from PyQt5.QtWidgets import QSizePolicy, QLabel, QAbstractButton, QGraphicsDropShadowEffect, QLineEdit, QLayoutItem
from PyQt5.QtWidgets import QPushButton, QStackedWidget, QLayout, QSpacerItem, QWidget, QComboBox, QProgressBar, QScrollArea, QFileDialog
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPaintEvent, QFontDatabase, QColor, QPen
from pyqtgraph import PlotDataItem, PlotWidget
import serial.tools.list_ports
import PyQt5.sip as sip
import config
import pandas as pd
import typing
from enum import Enum

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
    def __init__(self, text : str, font_idx : int, color_hex : str, scale : float = 1.0, parent : CustomMainWindow = None, percentSize : QSize = QSize(5, 5)):
        super().__init__(text, parent)
        
        self.__parent = parent
        self.percentSize = percentSize
        self.fontScale = scale
        
        font = QFont(QFontDatabase.applicationFontFamilies(font_idx)[0])

        self.setBgColor(color_hex)
        self.setFont(font)

        # responsive settings
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        self.setSizePolicy(sp)

        self.__parent.resized.connect(self.onResize)

        self.onResize()

    def setBgColor(self, color_hex):
        stylesheet = '''
            QLabel {{
                border-radius : 10px; 
                background-color: {color}; 
                padding: 10px;
            }}
            '''.format(color=color_hex)
        
        self.setStyleSheet(stylesheet)

    def onResize(self):
        self.setFixedSize(px(self.percentSize.width()), py(self.percentSize.height()))
        
    def resizeEvent(self, a0):
        new_font = self.font()
        new_font.setPointSize(py(self.fontScale))
        self.setFont(new_font)
        return super().resizeEvent(a0)
    
    def deleteLater(self):
        self.__parent.resized.disconnect(self.onResize)

        return super().deleteLater()
    
class AutoFontContentButton(QPushButton):
    def __init__(self, text : str = "", font_idx : int = None, color_hex : str = "#FA6FC3", scale : float = 1.0, percentSize = QSize(20, 10), parent : CustomMainWindow = None):
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
            QPushButton:checked {{
                background-color: gray; 
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
    def __init__(self, parent : CustomMainWindow  = None, percentSize : QSize = QSize(5, 10)):
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

class Screen:
    def __init__(self, name : str, showCallback, hideCallback):
        self.name = name
        self.showCB = showCallback
        self.hideCB = hideCallback

    def show(self):
        self.showCB()

    def hide(self):
        self.hideCB()

class ScreenNames:
    LAUNCH                  = "launch"
    HOME                    = "home"
    DEF_TAKE_SAMPLE         = "def-take-sample"
    DEF_MODEL_SELECTION     = "def-model-selection"
    DEF_PREDICTION_RESULT   = "def-prediction-result"
    CUS_GENOSE_SETTING      = "cus-genose-setting"
    CUS_TAKE_RAW            = "cus-take-raw"
    CUS_PREPROCESSING       = "cus-preprocessing" 
    CUS_FEATURE_SELECTION   = "cus-feature-selection"
    CUS_AI_MODEL            = "cus-ai-model"
    CUS_AI_EVALUATE         = "cus-ai-evaluate"
    CUS_TAKE_SAMPLE         = "cus-take-sample"
    CUS_MODEL_SELECTION     = "cus-model-selection"
    CUS_PREDICTION_RESULT   = "cus-predition-result"

class MainWindow(CustomMainWindow):
    take_data_sig = pyqtSignal()
    take_raw_sig = pyqtSignal()
    model_select_sig = pyqtSignal(str)
    ai_model_file_imported = pyqtSignal(str)
    inhale_flush_applied = pyqtSignal([int, int])
    preprocess_clicked = pyqtSignal()
    start_training_sig = pyqtSignal()

    def __init__(self, parent = ..., flags = ...):
        super(MainWindow, self).__init__()

        self.currentScreen = ScreenNames.LAUNCH

        self.screens = {
            ScreenNames.LAUNCH                : { "show" : self.showLaunchScreen,                      "hide" : self.hideLaunchScreen                      },
            ScreenNames.HOME                  : { "show" : self.showHomeContent,                       "hide" : self.hideHomeContent                       },
            ScreenNames.DEF_TAKE_SAMPLE       : { "show" : self.showDefaultTakeSampleContent,          "hide" : self.hideDefaultTakeSampleContent          },
            ScreenNames.DEF_MODEL_SELECTION   : { "show" : self.showDefaultModelSelectionContent,      "hide" : self.hideDefaultModelSelectionContent      },
            ScreenNames.DEF_PREDICTION_RESULT : { "show" : self.showDefaultPredictionResultContent,    "hide" : self.hideDefaultPredictionResultContent    },
            ScreenNames.CUS_GENOSE_SETTING    : { "show" : self.showCustomGenoseSettingContent,        "hide" : self.hideCustomGenoseSettingContent        },
            ScreenNames.CUS_TAKE_RAW          : { "show" : self.showCustomTakeDatasetContent,          "hide" : self.hideCustomTakeDatasetContent          },
            ScreenNames.CUS_PREPROCESSING     : { "show" : self.showCustomPreprocessingContent,        "hide" : self.hideCustomPreprocessingContent        },
            ScreenNames.CUS_FEATURE_SELECTION : { "show" : self.showCustomFeatureSelectContent,        "hide" : self.hideCustomFeatureSelectContent        },
            ScreenNames.CUS_AI_MODEL          : { "show" : self.showCustomAIModelContent,              "hide" : self.hideCustomAIModelContent              },
            ScreenNames.CUS_AI_EVALUATE       : { "show" : self.showCustomAIEvaluateContent,           "hide" : self.hideCustomAIEvaluateContent           },
            ScreenNames.CUS_TAKE_SAMPLE       : { "show" : self.showCustomTakeSampleContent,           "hide" : self.hideCustomTakeSampleContent           },
            ScreenNames.CUS_MODEL_SELECTION   : { "show" : self.showCustomModelSelectionContent,       "hide" : self.hideCustomModelSelectionContent       },
            ScreenNames.CUS_PREDICTION_RESULT : { "show" : self.showCustomPredictionResultContent,     "hide" : self.hideCustomPredictionResultContent     },
        }

        self.features = {"SKEW" : False, "KURTOSIS" : False, "MIN" : False, "MAX" : False, "MEAN" : False}

        self.aiModels : list[str] = []

        self.inhaleVal = 0.5
        self.flushVal = 20

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

        self.logo_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/etrainose_logo.png")
        self.home_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/home_icon.png")
        self.about_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/about_icon.png")
        self.botnav_next_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/next_button.png")
        self.botnav_prev_pixmap = QPixmap(f"{config.WORKING_DIR_PATH}/resources/prev_button.png")

        self.launchLogo = ResizedLogoLabel(self.launchPage)
        self.launchLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.launchLogo.setSourcePixmap(self.logo_pixmap)
        self.resized.connect(lambda: self.launchLogo.setGeometry(px(30), py(10), px(40), py(60)))

        self.appLogo = ResizedLogoLabel(self.appPage)
        self.appLogo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.appLogo.setSourcePixmap(self.logo_pixmap)
        self.resized.connect(lambda: self.appLogo.setGeometry(px(2), py(2), px(10), py(20)))

        self.homeButton = ClickableLabel(self.appPage)
        self.homeButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.homeButton.setSourcePixmap(self.home_pixmap)
        self.homeButton.clicked.connect(lambda: self.goToLaunch())
        self.homeButton.setToolTip("Kembali ke beranda")
        self.resized.connect(lambda: self.homeButton.setGeometry(px(2), py(82), px(10), py(10)))

        self.aboutButton = ClickableLabel(self.appPage)
        self.aboutButton.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.aboutButton.setSourcePixmap(self.about_pixmap)
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

        self.botNavNext = ClickableLabel(self)
        self.botNavNext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.botNavNext.setSourcePixmap(self.botnav_next_pixmap)
        self.botNavNext.clicked.connect(lambda: self.navToNext())
        self.resized.connect(lambda: self.botNavNext.setGeometry(px(85), py(85), px(10), py(10)))

        self.botNavPrev = ClickableLabel(self)
        self.botNavPrev.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.botNavPrev.setSourcePixmap(self.botnav_prev_pixmap)
        self.botNavPrev.clicked.connect(lambda: self.navToPrev())
        self.resized.connect(lambda: self.botNavPrev.setGeometry(px(75), py(85), px(10), py(10)))
        
        self.nextNav = ScreenNames.CUS_TAKE_RAW
        self.prevNav = ScreenNames.CUS_GENOSE_SETTING

        self.botNavNext.hide()
        self.botNavPrev.hide()

        self.isBotNavbarShown = False
        
        self.header = AutoFontLabel("HEADER", self.fonts[1], "#FA6FC3", 3.5, self, QSize(20, 10))
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.headerVbox.addWidget(self.header)

        self.footer = AutoFontLabel("FOOTER", self.fonts[1], "#FA6FC3", 2.5, self, QSize(30, 10))
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.footerVbox.addWidget(self.footer)

        self.notification = AutoFontLabel("Notification", self.fonts[2], "#FA6FC3", 1.5, self, QSize(40, 10))
        self.notification.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.notification.clicked.connect(lambda: print("notification clicked"))
        self.notification.setToolTip("Notification")
        self.resized.connect(lambda: self.notification.setGeometry(px(30), py(5), px(10), py(10)))
        self.opacity0(self.notification)

        self.infoBar = AutoFontLabel("Notification", self.fonts[2], "none", 1.0, self, QSize(30, 5))
        self.infoBar.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.resized.connect(lambda: self.infoBar.setGeometry(px(65), py(90), px(30), py(2)))
        self.infoBar.setText("")
    
    def findPorts(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.comboxPortSelector.addItem(port.name)

    def goToApp(self):
        self.pages.setCurrentIndex(1)
        self.changeContent(ScreenNames.HOME)

    def goToLaunch(self):
        self.pages.setCurrentIndex(0)
        self.hideBotNavbar()
        self.changeContent(ScreenNames.LAUNCH)
        self.currentScreen = ScreenNames.LAUNCH

    def navToNext(self):
        self.changeContent(self.nextNav)

    def navToPrev(self):
        self.changeContent(self.prevNav)

    def showHeader(self, text):
        self.header.setText(text)
        self.header.show()

    def hideHeader(self):
        self.header.hide()
    
    def showFooter(self, text):
        self.footer.setText(text)
        self.footer.show()

    def hideFooter(self):
        self.footer.hide()

    def showBotNavbar(self):
        self.isBotNavbarShown = True
        self.botNavNext.show()
        self.botNavPrev.show()
        
        
    def hideBotNavbar(self):
        self.isBotNavbarShown = False
        self.botNavNext.hide()
        self.botNavPrev.hide()

    def showLaunchScreen(self): ...
    def hideLaunchScreen(self): ...

    def showHomeContent(self):
        self.defaultButton = AutoFontContentButton(text="DEFAULT", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=3, parent=self)
        self.defaultButton.clicked.connect(lambda : self.changeContent(ScreenNames.DEF_TAKE_SAMPLE))

        # self.customButton = AutoFontContentButton(text="CUSTOM", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=3, parent=self)
        # self.customButton.clicked.connect(lambda : self.changeContent(ScreenNames.CUS_GENOSE_SETTING))

        self.contentVbox.addWidget(self.defaultButton)
        # self.contentVbox.addWidget(self.customButton)

        if(self.isBotNavbarShown):
            print("hello")
            self.hideBotNavbar()

        self.hideHeader()
        self.hideFooter()

    def hideHomeContent(self):
        self.defaultButton.deleteLater()
        # self.customButton.deleteLater()

    def showDefaultTakeSampleContent(self):
        self.takeDataButton = AutoFontContentButton(text="TAKE DATA SAMPLE", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=2, parent=self, percentSize=QSize(30, 10))
        # self.takeDataButton.clicked.connect(lambda : self.changeContent("def-model-selection"))
        self.takeDataButton.clicked.connect(lambda : self.take_data_sig.emit())

        self.sampleAmountEdit = AutoFontLineEdit(self, QSize(5,8))
        self.sampleAmountEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sampleAmountEdit.setText(str(10))

        self.showHeader("DEFAULT")

        self.dtkhlayout = QHBoxLayout()

        self.dtkhlayout.addWidget(self.takeDataButton)
        self.dtkhlayout.addWidget(self.sampleAmountEdit)

        self.contentVbox.addLayout(self.dtkhlayout)

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

        self.nextNav = ScreenNames.DEF_MODEL_SELECTION
        self.prevNav = ScreenNames.DEF_TAKE_SAMPLE

        self.showBotNavbar()
        

    def hideDefaultTakeSampleContent(self):
        self.barHbox.removeItem(self.spacer1)
        self.barHbox.removeItem(self.spacer2)
        self.takeDataButton.deleteLater()
        self.sampleAmountEdit.deleteLater()
        self.pbar.deleteLater()
        self.barHbox.deleteLater()
        self.dtkhlayout.deleteLater()

    def showDefaultModelSelectionContent(self):
        self.svmButton = AutoFontContentButton("SVM", self.fonts[1], "#FA6FC3", 2, QSize(25, 10), self)
        self.svmButton.clicked.connect(lambda : self.model_select_sig.emit("SVM"))

        self.rfButton = AutoFontContentButton("RANDOM FOREST", self.fonts[1], "#FA6FC3", 2, QSize(25, 10), self)
        self.rfButton.clicked.connect(lambda : self.model_select_sig.emit("RF"))

        self.nnButton = AutoFontContentButton("NN", self.fonts[1], "#FA6FC3", 2, QSize(25, 10), self)
        self.nnButton.clicked.connect(lambda : self.model_select_sig.emit("NN"))

        self.contentVbox.addWidget(self.svmButton)
        self.contentVbox.addWidget(self.rfButton)
        self.contentVbox.addWidget(self.nnButton)

        self.nextNav = ScreenNames.DEF_PREDICTION_RESULT
        self.prevNav = ScreenNames.DEF_TAKE_SAMPLE

    def hideDefaultModelSelectionContent(self):
        self.svmButton.deleteLater()
        self.rfButton.deleteLater()
        self.nnButton.deleteLater()

    def showDefaultPredictionResultContent(self):
        self.sensorGraph = PlotWidget(self.appPage)
        
        self.contentVbox.addWidget(self.sensorGraph)

        self.showFooter("PREDICTION RESULT")

        self.nextNav = ScreenNames.DEF_PREDICTION_RESULT
        self.prevNav = ScreenNames.DEF_MODEL_SELECTION
    
    def hideDefaultPredictionResultContent(self):
        self.sensorGraph.deleteLater()
        self.hideFooter()

    def showCustomGenoseSettingContent(self):
        self.showHeader("CUSTOM")

        def applyClicked():
            inhale = int (float(self.inhaleValEdit.text()) * 1000)
            flush = int (float(self.flushValEdit.text()) * 1000)

            self.inhale_flush_applied.emit(inhale, flush)
        
        self.inhaleLabel = AutoFontLabel("Inhale Timer (s)", self.fonts[1], "#D9D9D9", 2.0, self, QSize(23, 8))
        self.flushLabel = AutoFontLabel("Flush Timer (s)", self.fonts[1], "#D9D9D9", 2.0, self, QSize(23, 8))

        self.applyButton = AutoFontContentButton("apply", self.fonts[1], "#FA6FC3", 1.0, QSize(10, 6), self)
        self.applyButton.clicked.connect(applyClicked)

        self.inhaleValEdit = AutoFontLineEdit(self, QSize(5,8))
        self.inhaleValEdit.setText(str(self.inhaleVal))
        self.flushValEdit = AutoFontLineEdit(self, QSize(5,8))
        self.flushValEdit.setText(str(self.flushVal))

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

        self.nextNav = ScreenNames.CUS_TAKE_RAW
        self.prevNav = ScreenNames.CUS_GENOSE_SETTING

        self.showBotNavbar()

    def hideCustomGenoseSettingContent(self):
        self.clearContentVbox()

    def showCustomTakeDatasetContent(self): 
        self.takeDataButton = AutoFontContentButton(text="TAKE RAW DATASET", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=2, parent=self, percentSize=QSize(30, 10))
        self.takeDataButton.clicked.connect(lambda : self.take_raw_sig.emit())

        self.sampleAmountLabel = AutoFontLabel("Amount", self.fonts[1], "#FA6FC3", 2.0, self, QSize(10, 10))
        self.sampleAmountEdit = AutoFontLineEdit(self, QSize(18,10))
        self.sampleAmountEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sampleAmountEdit.setText("")
        self.sampleAmountEdit.setPlaceholderText("jumlah data")

        self.dtkhlayout = QHBoxLayout()
        self.dtkhlayout.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.dtkhlayout.addWidget(self.sampleAmountLabel)
        self.dtkhlayout.addWidget(self.sampleAmountEdit)

        self.trainingLabelLabel = AutoFontLabel("Label", self.fonts[1], "#FA6FC3", 2.0, self, QSize(10, 10))
        self.trainingLabelEdit = AutoFontLineEdit(self, QSize(18,10))
        self.trainingLabelEdit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trainingLabelEdit.setPlaceholderText("label data")
        self.trainingLabelEdit.setText("")

        self.trainingLabelHbox = QHBoxLayout()
        self.trainingLabelHbox.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.trainingLabelHbox.addWidget(self.trainingLabelLabel)
        self.trainingLabelHbox.addWidget(self.trainingLabelEdit)

        self.contentVbox.addLayout(self.dtkhlayout)
        self.contentVbox.addLayout(self.trainingLabelHbox)
        self.contentVbox.addWidget(self.takeDataButton)

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

        self.nextNav = ScreenNames.CUS_PREPROCESSING
        self.prevNav = ScreenNames.CUS_GENOSE_SETTING

    def hideCustomTakeDatasetContent(self):
        self.barHbox.removeItem(self.spacer1)
        self.barHbox.removeItem(self.spacer2)
        self.sampleAmountLabel.deleteLater()
        self.takeDataButton.deleteLater()
        self.sampleAmountEdit.deleteLater()
        self.pbar.deleteLater()
        self.barHbox.deleteLater()
        self.dtkhlayout.deleteLater()
        self.trainingLabelLabel.deleteLater()
        self.trainingLabelEdit.deleteLater()
        self.trainingLabelHbox.deleteLater()

    def showCustomPreprocessingContent(self): 
        self.preprocessingBtn = AutoFontContentButton("PREPROCESSING", self.fonts[1], "#FA6FC3", 2.0, QSize(25,10), self)
        self.preprocessingBtn.clicked.connect(lambda : self.preprocess_clicked.emit())

        self.contentVbox.addWidget(self.preprocessingBtn)

        self.nextNav = ScreenNames.CUS_FEATURE_SELECTION
        self.prevNav = ScreenNames.CUS_TAKE_RAW

    def hideCustomPreprocessingContent(self): 
        self.preprocessingBtn.deleteLater()

    def showCustomFeatureSelectContent(self): 
        self.featureSelectLabel = AutoFontLabel("FEATURE SELECTION", self.fonts[1], "#FA6FC3", 2.0, self, QSize(25,6))
        self.featureSelectLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.featureSelectLabelBox = QHBoxLayout()
        self.featureSelectLabelBox.addWidget(self.featureSelectLabel)

        self.featuresWidget = QWidget(self)
        self.featureScrollVbox = QVBoxLayout(self.featuresWidget)
        self.featureScrollVbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.featureScroll = QScrollArea(self)
        
        sp = self.featureScroll.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        
        self.featureScroll.setWidgetResizable(True)
        self.featureScroll.setSizePolicy(sp)
        self.featureScroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.featureScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.featureScroll.__onResize = lambda : self.featureScroll.setFixedSize(QSize(px(30),py(40)))
        self.featureScroll.__onResize()
        self.resized.connect(self.featureScroll.__onResize)
        self.featureScroll.setStyleSheet("QScrollArea { background-color:red; }")
        self.featuresWidget.setStyleSheet("QScrollArea { background-color:green; }")

        self.featureScroll.setWidget(self.featuresWidget)

        self.featureBtns : list[AutoFontContentButton] = []
        for fe in self.features.keys():
            feature = AutoFontContentButton(fe, self.fonts[1], "#FA6FC3", 2.0, QSize(20,8), self)
            feature.setCheckable(True)
            feature.setChecked(self.features[fe])

            self.featureBtns.append(feature)
            self.featureScrollVbox.addWidget(feature)

        # self.contentVbox.addWidget(self.featureSelectLabel)
        self.contentVbox.addLayout(self.featureSelectLabelBox)
        self.contentVbox.addWidget(self.featureScroll)

        self.nextNav = ScreenNames.CUS_AI_MODEL
        self.prevNav = ScreenNames.CUS_PREPROCESSING

    def hideCustomFeatureSelectContent(self): 
        self.featureSelectLabel.deleteLater()
        self.featureSelectLabelBox.deleteLater()
        for fe in self.featureBtns:
            key = fe.text()
            self.features[key] = fe.isChecked()
            fe.deleteLater()
        self.featuresWidget.deleteLater()
        self.resized.disconnect(self.featureScroll.__onResize)
        self.featureScroll.deleteLater()

    def showCustomAIModelContent(self): 
        def importModel():
            dir_ = QFileDialog.getOpenFileName(self, "Select python file", None, "Python file (*py)")
            self.ai_model_file_imported.emit(dir_[0])

        self.importModelBtn = AutoFontContentButton("IMPORT MODEL", self.fonts[1], "#FA6FC3", 2.0, QSize(25,10), self)
        self.importModelBtn.clicked.connect(lambda : importModel())

        self.startTrainingBtn = AutoFontContentButton("START TRAINING", self.fonts[1], "#FA6FC3", 2.0, QSize(25,10), self)

        self.startTrainingBtn.clicked.connect(lambda : self.start_training_sig.emit())

        self.contentVbox.addWidget(self.importModelBtn)
        self.contentVbox.addWidget(self.startTrainingBtn)

        self.nextNav = ScreenNames.CUS_AI_EVALUATE
        self.prevNav = ScreenNames.CUS_FEATURE_SELECTION

    def hideCustomAIModelContent(self): 
        self.importModelBtn.deleteLater()
        self.startTrainingBtn.deleteLater()

    def showCustomAIEvaluateContent(self): 
        self.modelEvaluationLbl = AutoFontLabel("MODEL EVALUATION", self.fonts[1], "#FA6FC3", 2.0, self, QSize(25,10))
        self.modelEvaluationLbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.modelEvaluation = AutoFontLabel("model accuracy is 1000%", self.fonts[1], "#FA6FC3", 1.0, self, QSize(25,10))
        self.modelEvaluation.setAlignment(Qt.AlignmentFlag.AlignJustify)

        self.contentVbox.addWidget(self.modelEvaluationLbl)
        self.contentVbox.addWidget(self.modelEvaluation)

        self.nextNav = ScreenNames.CUS_TAKE_SAMPLE
        self.prevNav = ScreenNames.CUS_AI_MODEL
    
    def hideCustomAIEvaluateContent(self): 
        self.modelEvaluation.deleteLater()
        self.modelEvaluationLbl.deleteLater()

    def showCustomTakeSampleContent(self): 
        self.takeDataButton = AutoFontContentButton(text="TAKE DATA SAMPLE", font_idx=self.fonts[1], color_hex="#FA6FC3", scale=2, parent=self, percentSize=QSize(30, 10))

        self.takeDataButton.clicked.connect(lambda : self.take_data_sig.emit())

        self.sampleAmountEdit = AutoFontLineEdit(self, QSize(5,8))
        self.sampleAmountEdit.setText(str(10))

        # self.comboxPortSelector = QComboBox()
        # self.findPorts()

        self.contentVbox.addWidget(self.takeDataButton)
        self.contentVbox.addWidget(self.sampleAmountEdit)
        # self.contentVbox.addWidget(self.comboxPortSelector)

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

        self.nextNav = ScreenNames.CUS_MODEL_SELECTION
        self.prevNav = ScreenNames.CUS_AI_EVALUATE

    def hideCustomTakeSampleContent(self):
        self.barHbox.removeItem(self.spacer1)
        self.barHbox.removeItem(self.spacer2)
        self.takeDataButton.deleteLater()
        # self.comboxPortSelector.deleteLater()
        self.pbar.deleteLater()
        self.barHbox.deleteLater()

    def showCustomModelSelectionContent(self): 
        self.aiModelButtons = []

        for i in range(0, len(self.aiModels)):
            model_key = self.aiModels[i]
            button = AutoFontContentButton(model_key, self.fonts[1], "#FA6FC3", 2, QSize(25, 10), self)

            button.clicked.connect(lambda checked, m=model_key: self.model_select_sig.emit(m))

            self.aiModelButtons.append(button)

        self.modelsWidget = QWidget(self)
        self.modelScrollVbox = QVBoxLayout(self.modelsWidget)
        self.modelScrollVbox.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.modelScroll = QScrollArea(self)
        
        sp = self.modelScroll.sizePolicy()
        sp.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        sp.setHorizontalPolicy(QSizePolicy.Policy.Fixed)
        
        self.modelScroll.setWidgetResizable(True)
        self.modelScroll.setSizePolicy(sp)
        self.modelScroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.modelScroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.modelScroll.__onResize = lambda : self.modelScroll.setFixedSize(QSize(px(30),py(40)))
        self.modelScroll.__onResize()
        self.resized.connect(self.modelScroll.__onResize)
        self.modelScroll.setStyleSheet("QScrollArea { background-color:red; }")
        self.modelsWidget.setStyleSheet("QScrollArea { background-color:green; }")

        self.modelScroll.setWidget(self.modelsWidget)

        for btn in self.aiModelButtons:
            self.modelScrollVbox.addWidget(btn)

        self.contentVbox.addWidget(self.modelScroll)

        self.nextNav = ScreenNames.CUS_PREDICTION_RESULT
        self.prevNav = ScreenNames.CUS_TAKE_SAMPLE

    def hideCustomModelSelectionContent(self): 
        for btn in self.aiModelButtons:
            btn.deleteLater()

        self.modelsWidget.deleteLater()
        self.resized.disconnect(self.modelScroll.__onResize)
        self.modelScroll.deleteLater()

    def showCustomPredictionResultContent(self): 
        self.sensorGraph = PlotWidget(self.appPage)
        
        self.contentVbox.addWidget(self.sensorGraph)

        self.showFooter("PREDICTION RESULT")

        self.nextNav = ScreenNames.CUS_PREDICTION_RESULT
        self.prevNav = ScreenNames.CUS_MODEL_SELECTION
    
    def hideCustomPredictionResultContent(self): 
        self.sensorGraph.deleteLater()
        self.hideFooter()

    def changeContent(self, dest):
        cur = self.currentScreen

        #cleanup last content
        cur_screen = self.screens.get(cur)

        if(cur_screen != None):
            hideFunc = cur_screen.get("hide")
            hideFunc()
        else:
            raise Exception(f"Current screen {cur} not found!")

        #show destination screen
        des_screen = self.screens.get(dest)

        if(des_screen != None):
            showFunc = des_screen.get("show")
            showFunc()
            self.currentScreen = dest
        else:
            raise Exception(f"Destination screen {cur} not found!")

    def opacity0(self, widget : QWidget):
        self.effect = QGraphicsOpacityEffect()
        self.effect.setOpacity(0.0)
        widget.setGraphicsEffect(self.effect)

    def notifyPopin(self, text):
        self.timer = QTimer()
        self.notification.setText(text)
        self.unfade(self.notification)
        self.timer.singleShot(2000, lambda: self.fade(self.notification))

    def fade(self, widget : QWidget):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def unfade(self, widget : QWidget):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

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

    def deleteChilds(self, obj):
        if issubclass(obj.__class__, QLayout):
            for i in reversed(range(obj.count())):
                child = obj.itemAt(i)

                self.deleteChilds(child)
                
                layout = obj.layout()
                layout.deleteLater()
                
        elif issubclass(obj.__class__, QWidgetItem):
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())