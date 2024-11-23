import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QProgressDialog, QDialog, QLineEdit, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5 import QtSerialPort
from PyQt5.QtGui import QPen, QColor
from PyQt5.uic.properties import QtWidgets
from pyqtgraph import PlotDataItem
# from Tools.i18n.pygettext import getFilesForName
from matplotlib import style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# import sip
from matplotlib.figure import Figure
import seaborn
from scipy.stats import skew, kurtosis
import pandas as pd
import numpy as np
from random import randint

from ai_start import NNClassifier, SVMClassifier, RFClassifier
from data_collector import DataCollector
import serial.tools.list_ports
import config

from mainwindowUI import Ui_MainWindow

DEFAULT_DATA_COLLECT_AMOUNT = 10

AI_MODEL_DICT = {
    "SVM" : 0,
    "NN" : 1,
    "RF" : 2
}

SUCCESS = 1

class matplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, dpi = 120):
        fig = Figure(dpi = dpi)
        self.axes = fig.add_subplot

class Genose(QObject):
    data_collection_finished = pyqtSignal(int)
    predict_finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.aiModel = None
        self.sensorData = None

    def __onDataCollectionFinish(self, datas : pd.DataFrame):
        self.sensorData = datas
        self.data_collection_finished.emit(SUCCESS)

    def __onPredictFinish(self, predictions):
        print(f"predictions : {predictions}")
        self.predict_finished.emit(SUCCESS)

    def setAIModel(self, model_id):
        model = None

        if(model_id == AI_MODEL_DICT["SVM"]):
            model = SVMClassifier()
            model.load(model_path=config.SVM_MODEL_PATH, label_encoder_path=config.SVM_LABEL_ENCODER_PATH)
            
        elif(model_id == AI_MODEL_DICT["NN"]):
            model = NNClassifier()
            model.load(model_path=config.NN_MODEL_PATH, label_encoder_path=config.NN_LABEL_ENCODER_PATH)

        elif(model_id == AI_MODEL_DICT["RF"]):
            model = RFClassifier()
            model.load(model_path=config.RF_MODEL_PATH, label_encoder_path=config.RF_LABEL_ENCODER_PATH)

        else:
            raise Exception("Model ID invalid")
        
        self.aiModel = model

    def __preproccessData(self, datas):
        # Function to extract features
        def __extractFeatures(data_chunk, sensor):
            return {
                f'MEAN_{sensor}': data_chunk[sensor].mean(),
                f'MIN_{sensor}': data_chunk[sensor].min(),
                f'MAX_{sensor}': data_chunk[sensor].max(),
                f'SKEW_{sensor}': skew(data_chunk[sensor]),
                f'KURT_{sensor}': kurtosis(data_chunk[sensor])
            }

        sensor_columns = ['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8','TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3']
        
        processed_data = pd.DataFrame()

        # Split data into chunks of 156 rows
        num_chunks = len(datas) // 156

        for i in range(num_chunks):
            data_chunk = datas.iloc[i * 156:(i + 1) * 156]
            features = {}

            # Extract features for each sensor
            for sensor in sensor_columns:
                features.update(__extractFeatures(data_chunk, sensor))

            dfeatures = pd.DataFrame(features, index=[0])

            # Append to the final DataFrame
            processed_data = pd.concat([dfeatures, processed_data])

        return processed_data

    def startCollectData(self, port, amount = DEFAULT_DATA_COLLECT_AMOUNT):
        self.data_collection_thread = DataCollectionThread()
        self.data_collection_thread.finished.connect(self.__onDataCollectionFinish)
        self.data_collection_thread.setPort(port=port)
        self.data_collection_thread.setAmount(amount=amount)
        self.data_collection_thread.start()

    def startPredict(self):
        self.predict_thread = PredictionThread()
        self.predict_thread.finished.connect(self.__onPredictFinish)
        self.predict_thread.setAIModel(self.aiModel)
        
        preprocessed_data = self.__preproccessData(self.sensorData)
        self.predict_thread.setDatas(preprocessed_data)
        
        self.predict_thread.start()
    

class DataCollectionThread(QThread):
    finished = pyqtSignal(pd.DataFrame)

    def setPort(self, port: str):
        self.port = port

    def setAmount(self, amount: int):
        self.amount = amount

    def run(self):
        try:
            print(f"Collecting from port {self.port} with amount {self.amount}")
            # Pass the amount parameter when initializing DataCollector
            self.data_collector = DataCollector(port=self.port, amount=self.amount)
            self.data_collector.initialize()
            self.data_collector.collect()
            # self.data_collector.save(filename='file.csv')
            datas = self.data_collector.getDataFrame()

        except FileNotFoundError as e:
            print(f"cant access port {self.port}")

        except Exception as e:
            print(f"Error during data collection: {e}")

        finally:
            self.finished.emit(datas)

class PredictionThread(QThread):
    finished = pyqtSignal(np.ndarray)

    def setAIModel(self, model):
        self.model = model

    def setDatas(self, datas : pd.DataFrame):
        self.datas = datas

    def run(self):
        try:
            predictions = self.model.predict(self.datas)
            print(predictions)
        
        except Exception as e:
            print(f"Error during prediction: {e}")

        finally:
            self.finished.emit(predictions)

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

        self.genose = Genose()
        self.genose.data_collection_finished.connect(self.on_data_collection_finished)
        self.genose.predict_finished.connect(self.on_prediction_finished)

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
        # Create and configure the progress dialog
        self.progress_dialog = QProgressDialog("Predicting...", None, 0, 0, self.main_win)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        model_id = AI_MODEL_DICT["SVM"]

        self.genose.setAIModel(model_id)
        self.genose.startPredict()

    def on_data_collection_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        QMessageBox.information(self.main_win, "Data Collection", "Data collection completed successfully!")

    def on_prediction_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        
        self.plot_sensor_data(sensor_datas=self.genose.sensorData)
        
        QMessageBox.information(self.main_win, "Prediction", "Prediction completed successfully!")

    def csv_import(self):
        filePath = QFileDialog.getOpenFileName(filter="csv (*.csv)")[0]

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

        self.ui.grph_default_result.plotItem.clear()

        for sensor_key in sensor_colors.keys():
            sensor_data = sensor_datas[sensor_key].to_list()

            pen = QPen()
            pen.setWidthF(0.05)
            pen.setColor(sensor_colors[sensor_key])
            
            self.ui.grph_default_result.plotItem.addItem(
                PlotDataItem(y=sensor_data, pen=pen)
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
