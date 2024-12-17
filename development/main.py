import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QThread, QThreadPool

from lib.genose.genose import Genose, PREDICT_RESULT_DICT, FindPortWorker

from main_window import MainWindow

class AppWindow(MainWindow):
    def __init__(self, parent=..., flags=...):
        super().__init__(parent, flags)

        self.importedAiModule = None

        self.startButton.setText("LOADING")
        self.startButton.setEnabled(False)
        self.startButton.setDown(True)

        self.aboutButton.clicked.connect(lambda : print("info"))

        self.take_data_sig.connect(self.collect_data_with_loading)
        self.take_raw_sig.connect(self.collect_raw_data_with_loading)
        self.model_select_sig.connect(self.model_predict_with_loading)
        self.ai_model_file_imported.connect(self.ai_model_file_import)
        self.inhale_flush_applied.connect(self.on_inhale_flush_applied)
        self.preprocess_clicked.connect(self.preprocessing)
        self.start_training_sig.connect(self.start_training)

        self.genose = Genose()
        self.genose.loadModelsFromFolder()
        self.genose.findGenosePort()

        for mdl in self.genose.DEFAULT_AI_DICT.keys():
            self.aiModels.append(mdl)

        for mdl in self.genose.CUSTOM_AI_DICT.keys():
            self.aiModels.append(mdl)
        
        self.genose.genose_port_search_finished.connect(self.on_genose_port_finished)
        self.genose.genose_port_search_progress.connect(self.on_genose_port_progress)
        self.genose.data_collection_progress.connect(self.on_data_collection_progress)
        self.genose.predict_finished.connect(self.on_prediction_finished)

        self.timer = QTimer()

    def on_inhale_flush_applied(self, inhale, flush):
        self.genose.setInhaleFlushTimerSetting(port= self.selectedPort,inhale= inhale, flush= flush)

    def collect_data_with_loading(self):
        print("Collecting data")
        selectedPort = self.selectedPort
        selectAmount = int(self.sampleAmountEdit.text())

        if(selectAmount <= 0):
            # need to display error
            return
        
        self.takeDataButton.setDisabled(True)

        self.genose.data_collection_finished.connect(self.on_data_collection_finished)
        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def collect_raw_with_loading(self):
        print("Collecting data")
        selectedPort = self.selectedPort
        selectAmount = int(self.sampleAmountEdit.text())

        if(selectAmount <= 0):
            # need to display error
            return
        
        self.takeDataButton.setDisabled(True)

        self.genose.data_collection_finished.connect(self.on_raw_data_collection_finished)
        self.genose.startCollectData(port=selectedPort, amount=selectAmount)

    def model_predict_with_loading(self, model_id : str):
        print(f"Predicting using {model_id}")
        self.genose.setAIModel(model_id)
        self.genose.startPredict()

    def preprocessing(self):
        print("preprocessing")

    def start_training(self):
        print(f"start training")
        print(f"using features : {self.features}")
        print(f"using model : {self.importedAiModule}")

        self.genose.startTraining(self.importedAiModule, self.features)

    def ai_model_file_import(self, model_filepath):
        module = self.genose.loadModelModuleFromFile(model_filepath, "model")

        if(module == None):
            self.notifyPopin("Model invalid!")
            self.notification.setBgColor("red")
        else:
            self.notifyPopin("Model loaded successfully")
            self.notification.setBgColor("blue")
        
        self.importedAiModule = module

    def on_genose_port_finished(self, port):
        self.infoBar.setText(f"selected genose port : {port}")
        self.timer.singleShot(2000, lambda: self.infoBar.setText(""))

        if(port==""):
            self.notifyPopin("No Genose Found")
            self.timer.singleShot(5000, lambda: self.genose.findGenosePort())

        else:
            self.selectedPort = port
            self.startButton.setText("START")
            self.startButton.setEnabled(True)
            self.startButton.setDown(False)

    def on_genose_port_progress(self, progress):
        self.infoBar.setText(f"genose search progress : {progress}%")

    def on_data_collection_finished(self):
        self.takeDataButton.setDisabled(False)
        self.pbar.setValue(100)
        # self.changeContent("def-model-selection")
        self.notifyPopin("Finished collecting data")

    def on_raw_data_collection_finished(self):
        self.takeDataButton.setDisabled(False)
        self.pbar.setValue(100)
        
        self.notifyPopin("Finished collecting raw data")

        label = self.trainingLabelEdit.text()
        
        self.genose.sensorData["LABEL"] = label

    def on_data_collection_progress(self, progress):
        self.pbar.setValue(progress)

    def on_prediction_finished(self):
        self.changeContent("def-prediction-result")
        
        result = self.genose.predictions[len(self.genose.predictions) - 1]
        result = PREDICT_RESULT_DICT[result]

        self.footer.setText(result)
        
        self.plot_sensor_data(self.genose.sensorData)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = AppWindow()
    main_win.show()
    sys.exit(app.exec_())
