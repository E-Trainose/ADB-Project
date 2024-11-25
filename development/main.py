import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog, QDialog, QLineEdit, QFileDialog, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QColor
from PyQt5.uic.properties import QtWidgets
from pyqtgraph import PlotDataItem
import seaborn
import pandas as pd
import numpy as np
from random import randint

from genose import Genose, AI_MODEL_DICT
from graph_canvas import GraphCanvas

import serial.tools.list_ports

from mainwindowUI import Ui_MainWindow

class MainWindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_win)

        self.ui.stackedWidget.setCurrentWidget(self.ui.pg_home)
        self.ui.btn_default.clicked.connect(self.show_default)
        self.ui.btn_custom.clicked.connect(self.show_custom)
        self.ui.btn_default_take.clicked.connect(self.collect_data_with_loading)
        self.ui.btn_default_svm.clicked.connect(self.svm_model_predict_with_loading)
        self.ui.btn_default_nn.clicked.connect(self.nn_model_predict_with_loading)
        self.ui.btn_default_rf.clicked.connect(self.rf_model_predict_with_loading)
        self.ui.btn_page_home.clicked.connect(self.show_first_page)
        self.ui.btn_custom_take_1.clicked.connect(self.show_custom_gauss)
        self.ui.btn_custom_gauss.clicked.connect(self.show_custom_feat)
        self.ui.btn_custom_feat_done.clicked.connect(self.show_custom_algo)
        self.ui.btn_default_take_next.clicked.connect(self.show_default_algo)
        self.ui.btn_default_algo_next.clicked.connect(self.show_default_result)
        self.ui.btn_default_algo_back.clicked.connect(self.show_first_page)
        self.ui.btn_default_result_back.clicked.connect(self.show_default_algo)
        
        self.findPorts()

        self.genose = Genose()
        self.genose.data_collection_finished.connect(self.on_data_collection_finished)
        self.genose.predict_finished.connect(self.on_prediction_finished)

        self.graph_canvas = GraphCanvas(self.main_win)
        graph_layout = QVBoxLayout(self.ui.grph_default_result)
        graph_layout.addWidget(self.graph_canvas)

    def findPorts(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(port.name)
            self.ui.combox_serialport_selector.addItem(port.name)

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
        # Retrieve the user input
        selectedPort = self.ui.combox_serialport_selector.currentText()
        selectAmount = self.ui.inputamount_default_take.value()  # Ensure this retrieves an integer

        if(selectAmount <= 0):
            # need to display error
            return
        
        # Create and configure the progress dialog
        self.progress_dialog = QProgressDialog("Collecting data...", None, 0, 0, self.main_win)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def svm_model_predict_with_loading(self):
        self.model_predict_with_loading(model_id=AI_MODEL_DICT['SVM'])
    
    def nn_model_predict_with_loading(self):
        self.model_predict_with_loading(model_id=AI_MODEL_DICT['NN'])

    def rf_model_predict_with_loading(self):
        self.model_predict_with_loading(model_id=AI_MODEL_DICT['RF'])

    def model_predict_with_loading(self, model_id):
        # Create and configure the progress dialog
        self.progress_dialog = QProgressDialog("Predicting...", None, 0, 0, self.main_win)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        self.genose.setAIModel(model_id)
        self.genose.startPredict()

    def on_data_collection_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        QMessageBox.information(self.main_win, "Data Collection", "Data collection completed successfully!")

    def on_prediction_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        
        # self.plot_sensor_data(sensor_datas=self.genose.sensorData)
        self.graph_canvas.update_plot(self.genose.sensorData)
        
        QMessageBox.information(self.main_win, "Prediction", "Prediction completed successfully!")

    # def csv_import(self):
    #     filePath = QFileDialog.getOpenFileName(filter="csv (*.csv)")[0]

    # def plot_sensor_data(self, sensor_datas : pd.DataFrame):
    #     sensor_colors = {
    #         'TGS2600'   : QColor(255, 255, 255, 127), 
    #         'TGS2602'   : QColor(255, 255, 0, 127), 
    #         'TGS816'    : QColor(0, 0, 255, 127), 
    #         'TGS813'    : QColor(255, 0, 0, 127), 
    #         'MQ8'       : QColor(255, 255, 255, 127),
    #         'TGS2611'   : QColor(255, 255, 0, 127), 
    #         'TGS2620'   : QColor(0, 0, 255, 127), 
    #         'TGS822'    : QColor(0, 255, 0, 127), 
    #         'MQ135'     : QColor(0, 255, 255, 127), 
    #         'MQ3'       : QColor(105, 100, 140, 127)
    #     }

    #     self.ui.grph_default_result.plotItem.clear()

    #     for sensor_key in sensor_colors.keys():
    #         sensor_data = sensor_datas[sensor_key].to_list()

    #         pen = QPen()
    #         pen.setWidthF(0.1)
    #         pen.setColor(sensor_colors[sensor_key])
            
    #         self.ui.grph_default_result.plotItem.addItem(
    #             PlotDataItem(
    #                 y=sensor_data, 
    #                 pen=pen
    #             )
    #         )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
