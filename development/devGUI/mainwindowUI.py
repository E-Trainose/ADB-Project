# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindowui.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1127, 768)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralwidget)
        self.stackedWidget.setGeometry(QtCore.QRect(19, 9, 1091, 671))
        self.stackedWidget.setObjectName("stackedWidget")
        self.pg_home = QtWidgets.QWidget()
        self.pg_home.setObjectName("pg_home")
        self.stackedWidget.addWidget(self.pg_home)
        self.pg_default = QtWidgets.QWidget()
        self.pg_default.setObjectName("pg_default")
        self.stackedWidget_2 = QtWidgets.QStackedWidget(self.pg_default)
        self.stackedWidget_2.setGeometry(QtCore.QRect(20, 50, 1051, 581))
        self.stackedWidget_2.setObjectName("stackedWidget_2")
        self.pg_default_take = QtWidgets.QWidget()
        self.pg_default_take.setObjectName("pg_default_take")
        self.btn_default_take = QtWidgets.QPushButton(self.pg_default_take)
        self.btn_default_take.setGeometry(QtCore.QRect(440, 240, 171, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.btn_default_take.setFont(font)
        self.btn_default_take.setObjectName("btn_default_take")
        self.stackedWidget_2.addWidget(self.pg_default_take)
        self.pg_default_algo = QtWidgets.QWidget()
        self.pg_default_algo.setObjectName("pg_default_algo")
        self.btn_default_nn = QtWidgets.QPushButton(self.pg_default_algo)
        self.btn_default_nn.setGeometry(QtCore.QRect(440, 140, 201, 81))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.btn_default_nn.setFont(font)
        self.btn_default_nn.setObjectName("btn_default_nn")
        self.btn_default_svm = QtWidgets.QPushButton(self.pg_default_algo)
        self.btn_default_svm.setGeometry(QtCore.QRect(440, 230, 201, 71))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.btn_default_svm.setFont(font)
        self.btn_default_svm.setObjectName("btn_default_svm")
        self.btn_default_rf = QtWidgets.QPushButton(self.pg_default_algo)
        self.btn_default_rf.setGeometry(QtCore.QRect(440, 310, 201, 71))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.btn_default_rf.setFont(font)
        self.btn_default_rf.setObjectName("btn_default_rf")
        self.stackedWidget_2.addWidget(self.pg_default_algo)
        self.pg_default_result = QtWidgets.QWidget()
        self.pg_default_result.setObjectName("pg_default_result")
        self.grph_default_result = QtWidgets.QGraphicsView(self.pg_default_result)
        self.grph_default_result.setGeometry(QtCore.QRect(110, 20, 821, 401))
        self.grph_default_result.setMidLineWidth(0)
        self.grph_default_result.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.grph_default_result.setObjectName("grph_default_result")
        self.stackedWidget_2.addWidget(self.pg_default_result)
        self.label = QtWidgets.QLabel(self.pg_default)
        self.label.setGeometry(QtCore.QRect(490, 10, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.stackedWidget.addWidget(self.pg_default)
        self.pg_custom = QtWidgets.QWidget()
        self.pg_custom.setObjectName("pg_custom")
        self.stackedWidget_3 = QtWidgets.QStackedWidget(self.pg_custom)
        self.stackedWidget_3.setGeometry(QtCore.QRect(30, 40, 1031, 601))
        self.stackedWidget_3.setObjectName("stackedWidget_3")
        self.pg_custom_take_1 = QtWidgets.QWidget()
        self.pg_custom_take_1.setObjectName("pg_custom_take_1")
        self.stackedWidget_3.addWidget(self.pg_custom_take_1)
        self.pg_custom_gauss = QtWidgets.QWidget()
        self.pg_custom_gauss.setObjectName("pg_custom_gauss")
        self.stackedWidget_3.addWidget(self.pg_custom_gauss)
        self.pg_custom_feat_select = QtWidgets.QWidget()
        self.pg_custom_feat_select.setObjectName("pg_custom_feat_select")
        self.stackedWidget_3.addWidget(self.pg_custom_feat_select)
        self.pg_custom_model_train = QtWidgets.QWidget()
        self.pg_custom_model_train.setObjectName("pg_custom_model_train")
        self.stackedWidget_3.addWidget(self.pg_custom_model_train)
        self.pg_custom_take_2 = QtWidgets.QWidget()
        self.pg_custom_take_2.setObjectName("pg_custom_take_2")
        self.stackedWidget_3.addWidget(self.pg_custom_take_2)
        self.pg_custom_algo = QtWidgets.QWidget()
        self.pg_custom_algo.setObjectName("pg_custom_algo")
        self.stackedWidget_3.addWidget(self.pg_custom_algo)
        self.pg_custom_result = QtWidgets.QWidget()
        self.pg_custom_result.setObjectName("pg_custom_result")
        self.stackedWidget_3.addWidget(self.pg_custom_result)
        self.stackedWidget.addWidget(self.pg_custom)
        self.btn_default = QtWidgets.QPushButton(self.centralwidget)
        self.btn_default.setGeometry(QtCore.QRect(20, 690, 75, 23))
        self.btn_default.setObjectName("btn_default")
        self.btn_custom = QtWidgets.QPushButton(self.centralwidget)
        self.btn_custom.setGeometry(QtCore.QRect(1030, 690, 75, 23))
        self.btn_custom.setObjectName("btn_custom")
        self.btn_page_home = QtWidgets.QPushButton(self.centralwidget)
        self.btn_page_home.setGeometry(QtCore.QRect(530, 690, 93, 28))
        self.btn_page_home.setObjectName("btn_page_home")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1127, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btn_default_take.setText(_translate("MainWindow", "TAKE DATA"))
        self.btn_default_nn.setText(_translate("MainWindow", "NN"))
        self.btn_default_svm.setText(_translate("MainWindow", "SVM"))
        self.btn_default_rf.setText(_translate("MainWindow", "Random Forest"))
        self.label.setText(_translate("MainWindow", "DEFAULT"))
        self.btn_default.setText(_translate("MainWindow", "default"))
        self.btn_custom.setText(_translate("MainWindow", "custom"))
        self.btn_page_home.setText(_translate("MainWindow", "home"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
