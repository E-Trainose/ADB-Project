from classifier import BaseClassifier, NNClassifier, SVMClassifier, RFClassifier, PredictionThread
from data_collector import DataCollectionThread
import config
import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject

DEFAULT_DATA_COLLECT_AMOUNT = 10

AI_MODEL_DICT = {
    "SVM" : 0,
    "NN" : 1,
    "RF" : 2
}

SUCCESS = 1

class Genose(QObject):
    data_collection_finished = pyqtSignal(int)
    data_collection_progress = pyqtSignal(int)
    predict_finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.aiModel = None
        self.sensorData = None

    def __onDataCollectionFinish(self, datas : pd.DataFrame):
        self.sensorData = datas
        self.data_collection_finished.emit(SUCCESS)

    def __onDataCollectionProgress(self, progress : int):
        self.data_collection_progress.emit(progress)

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

    def startCollectData(self, port, amount = DEFAULT_DATA_COLLECT_AMOUNT):
        self.data_collection_thread = DataCollectionThread()
        self.data_collection_thread.finished.connect(self.__onDataCollectionFinish)
        self.data_collection_thread.progress.connect(self.__onDataCollectionProgress)
        self.data_collection_thread.setPort(port=port)
        self.data_collection_thread.setAmount(amount=amount)
        self.data_collection_thread.start()

    def startPredict(self):
        self.predict_thread = PredictionThread()
        self.predict_thread.finished.connect(self.__onPredictFinish)
        self.predict_thread.setAIModel(self.aiModel)
        
        self.predict_thread.setDatas(self.sensorData)
        
        self.predict_thread.start()