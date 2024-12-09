import sys
from PyQt5.QtWidgets import QApplication

from genose import Genose, AI_MODEL_DICT, PREDICT_RESULT_DICT

from main_window import MainWindow

class AppWindow(MainWindow):
    def __init__(self, parent=..., flags=...):
        super().__init__(parent, flags)

        self.aboutButton.clicked.connect(lambda : print("info"))

        self.take_data_sig.connect(self.collect_data_with_loading)
        self.model_select_sig.connect(self.model_predict_with_loading)
        self.ai_model_file_imported.connect(self.ai_model_file_import)

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
        
        self.takeDataButton.setDisabled(True)

        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def model_predict_with_loading(self, model_id):
        self.genose.setAIModel(model_id)
        self.genose.startPredict()

    def ai_model_file_import(self, model_filepath):
        module = self.genose.loadModelModuleFromFile(model_filepath, "model")

        if(module == None):
            self.notifyPopin("Model invalid!")
            self.notification.setBgColor("red")
        else:
            self.notifyPopin("Model loaded successfully")
            self.notification.setBgColor("blue")


    def on_data_collection_finished(self):
        self.takeDataButton.setDisabled(False)
        self.pbar.setValue(100)
        self.changeContent("def-model-selection")

    def on_data_collection_progress(self, progress):
        self.pbar.setValue(progress)

    def on_prediction_finished(self):
        self.changeContent("def-prediction-result")
        
        result = self.genose.predictions[len(self.genose.predictions) - 1]
        result = PREDICT_RESULT_DICT[result]

        self.header.setText(result)
        
        self.plot_sensor_data(self.genose.sensorData)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AppWindow()
    main_win.show()
    sys.exit(app.exec_())
