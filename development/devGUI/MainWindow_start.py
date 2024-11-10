import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow

from mainwindowUI import Ui_MainWindow

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_home)
        self.ui.btn_default.clicked.connect(self.show_default)
        self.ui.btn_custom.clicked.connect(self.show_custom)
        self.ui.btn_default_take.clicked.connect(self.show_default_algo)


    def show(self):
        self.main_win.show()

    def show_default(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_default)
    def show_custom(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_custom)
    def show_default_algo(self):
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.pg_default_algo)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())