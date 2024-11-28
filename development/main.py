import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.uic.properties import QtWidgets
from pyqtgraph import PlotDataItem
import seaborn
import pandas as pd
import numpy as np
from random import randint

from genose import Genose, AI_MODEL_DICT
from graph_canvas import GraphCanvas

from main_window import MainWindow

class AppWindow(MainWindow):
    def __init__(self, parent=..., flags=...):
        super().__init__(parent, flags)

        self.aboutButton.clicked.connect(lambda : print("info"))

        self.take_data_sig.connect(lambda: self.collect_data_with_loading())
        self.model_select_sig.connect(lambda: self.svm_model_predict_with_loading())

        self.genose = Genose()
        
        self.genose.data_collection_finished.connect(self.on_data_collection_finished)
        self.genose.data_collection_progress.connect(self.on_data_collection_progress)
        self.genose.predict_finished.connect(self.on_prediction_finished)

    def collect_data_with_loading(self):
        print("Collecting data")
        # Retrieve the user input
        selectedPort = self.comboxPortSelector.currentText()
        # selectAmount = self.ui.inputamount_default_take.value()  # Ensure this retrieves an integer
        selectAmount = 5

        if(selectAmount <= 0):
            # need to display error
            return

        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def svm_model_predict_with_loading(self):
        self.model_predict_with_loading(model_id=AI_MODEL_DICT['SVM'])

    def model_predict_with_loading(self, model_id):
        self.genose.setAIModel(model_id)
        self.genose.startPredict()

    def on_data_collection_finished(self):
        self.pbar.setValue(100)
        self.changeContent("def-model-selection")

    def on_data_collection_progress(self, progress):
        self.pbar.setValue(progress)

    def on_prediction_finished(self):
        self.changeContent("def-prediction-result")
        self.plot_sensor_data(self.genose.sensorData)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AppWindow()
    main_win.show()
    sys.exit(app.exec_())
