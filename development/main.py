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

        self.genose = Genose()
        
        self.genose.data_collection_finished.connect(self.on_data_collection_finished)
        self.genose.predict_finished.connect(self.on_prediction_finished)

    def collect_data_with_loading(self):
        # Retrieve the user input
        selectedPort = self.comboxPortSelector.currentText()
        # selectAmount = self.ui.inputamount_default_take.value()  # Ensure this retrieves an integer
        selectAmount = 5

        if(selectAmount <= 0):
            # need to display error
            return
        
        # Create and configure the progress dialog
        self.progress_dialog = QProgressDialog("Collecting data...", None, 0, 0, self)
        self.progress_dialog.setWindowTitle("Please Wait")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setRange(0, 0)
        self.progress_dialog.show()

        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def on_data_collection_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        QMessageBox.information(self, "Data Collection", "Data collection completed successfully!")
        
        self.changeContent("def-model-selection")

    def on_prediction_finished(self):
        # Close the progress dialog when data collection is done
        self.progress_dialog.close()
        
        # self.plot_sensor_data(sensor_datas=self.genose.sensorData)
        # self.graph_canvas.update_plot(self.genose.sensorData)
        
        QMessageBox.information(self, "Prediction", "Prediction completed successfully!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AppWindow()
    main_win.show()
    sys.exit(app.exec_())
