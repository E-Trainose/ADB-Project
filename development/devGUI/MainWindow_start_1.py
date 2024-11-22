import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog, QDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5 import QtSerialPort
from PyQt5.uic.properties import QtWidgets
from Tools.i18n.pygettext import getFilesForName
from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import sip
from matplotlib.figure import Figure
import seaborn
import pandas as pd


from data_collector import DataCollector
import serial.tools.list_ports

from mainwindowUI import Ui_MainWindow

class matplotlibCanvas(FigureCanvas)
    def __init__(self, parent=None, dpi = 120):
        fig = figure(dpi = dpi)
        self.axes = fig.add_subplot

class DataCollectionThread(QThread):
    finished = pyqtSignal()

    def setPort(self, port: str):
        self.port = port

    def setAmount(self, amount: int):
        self.amount = amount

    def run(self):
        try:
            print(f"Collecting from port {self.port} with amount {self.amount}")
            # Pass the amount parameter when initializing DataCollector
            dCol = DataCollector(port=self.port, amount=self.amount)
            dCol.collect(amount=self.amount)
            dCol.save(filename='file.csv')
        except Exception as e:
            print(f"Error during data collection: {e}")
        finally:
            self.finished.emit()




class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_home)
        self.ui.btn_default.clicked.connect(self.show_default)
        self.ui.btn_custom.clicked.connect(self.show_custom)
        self.ui.btn_default_take.clicked.connect(self.collect_data_with_loading)
        self.ui.btn_default_svm.clicked.connect(self.show_default_result)
        self.ui.btn_default_nn.clicked.connect(self.show_default_result)
        self.ui.btn_default_rf.clicked.connect(self.show_default_result)
        self.ui.btn_page_home.clicked.connect(self.show_first_page)
        self.ui.btn_custom_take_1.clicked.connect(self.show_custom_gauss)
        self.ui.btn_custom_gauss.clicked.connect(self.show_custom_feat)
        self.ui.btn_custom_feat_done.clicked.connect(self.show_custom_algo)
        self.ui.btn_default_take_next.clicked.connect(self.show_default_algo)
        self.ui.btn_default_algo_next.clicked.connect(self.show_default_result)
        self.ui.btn_default_algo_back.clicked.connect(self.show_first_page)
        self.ui.btn_default_result_back.clicked.connect(self.show_default_algo)
        self.findPorts()

    def findPorts(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(port.name)
            self.ui.combox_serialport_selector.addItem(port.name)

    def init


    def show(self):
        self.main_win.show()

    def show_default(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_default)

    def show_custom(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_custom)

    def show_custom_gauss(self):
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.pg_custom_gauss)

    def show_custom_feat(self):
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.pg_custom_feat_select)

    def show_default_algo(self):
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.pg_default_algo)

    def show_default_result(self):
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.pg_default_result)

    def show_first_page(self):
        self.ui.stackedWidget_2.setCurrentWidget(self.ui.pg_default_take)
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.pg_custom_take_1)

    def show_custom_algo(self):
        self.ui.stackedWidget_3.setCurrentWidget(self.ui.pg_custom_model_train)

    def collect_data_with_loading(self):
        # Create and configure the progress dialog
        self.progress_dialog = QProgressDialog("Collecting data...", None, 0, 0, self.main_win)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        # Retrieve the user input
        selectedPort = self.ui.combox_serialport_selector.currentText()
        selectAmount = self.ui.inputamount_default_take.value()  # Ensure this retrieves an integer

        # Start the data collection thread
        self.data_thread = DataCollectionThread()
        self.data_thread.setPort(port=selectedPort)
        self.data_thread.setAmount(amount=selectAmount)
        self.data_thread.finished.connect(self.on_data_collection_finished)
        self.data_thread.start()

    def on_data_collection_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        QMessageBox.information(self.main_win, "Data Collection", "Data collection completed successfully!")

    def csv_import(self):
        filePath = QFileDialog.getOpenFileName(filter="csv (*.csv)")[0]
        pri
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
