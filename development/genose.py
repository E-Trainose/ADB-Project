import sys, os
from classifier import BaseClassifier, NNClassifier, SVMClassifier, RFClassifier, PredictionThread
from data_collector import DataCollectionThread
import config
import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
import importlib.util
import sys
import string
import secrets

DEFAULT_DATA_COLLECT_AMOUNT = 10

AI_MODEL_DICT = {
    "SVM" : {
        "model" : SVMClassifier,
        "paths" :{
            "model" : config.SVM_MODEL_PATH,
            "label_encoder" : config.SVM_LABEL_ENCODER_PATH
        }
    },
    "NN" : {
        "model" : NNClassifier,
        "paths" :{
            "model" : config.NN_MODEL_PATH,
            "label_encoder" : config.NN_LABEL_ENCODER_PATH
        }
    },
    "RF" : {
        "model" : RFClassifier,
        "paths" :{
            "model" : config.RF_MODEL_PATH,
            "label_encoder" : config.RF_LABEL_ENCODER_PATH
        }
    }
}

PREDICT_RESULT_DICT = { # TODO : This
    0 : "KOPI",
    10 : "TEH",
    100 : "JAGUNG"
}

SUCCESS = 1

def gensym(length=32, prefix="gensym_"):
        """
        generates a fairly unique symbol, used to make a module name,
        used as a helper function for load_module

        :return: generated symbol
        """
        alphabet = string.ascii_uppercase + string.ascii_lowercase + string.digits
        symbol = "".join([secrets.choice(alphabet) for i in range(length)])

        return prefix + symbol

def load_module(source, module_name=None):
    """
    reads file source and loads it as a module

    :param source: file to load
    :param module_name: name of module to register in sys.modules
    :return: loaded module
    """

    if module_name is None:
        module_name = gensym()

    spec = importlib.util.spec_from_file_location(module_name, source)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module

def read_files(dir : str):
    results = {}
    for dirpath, dnames, fnames in os.walk(dir):
        name = dirpath.replace(dir, "").replace("\\", "").replace("/", "").upper()

        if(dirpath.find("__pycache__") > -1):
            continue

        if(name == ""):
            continue
        
        result = {}

        for f in fnames:
            path = os.path.join(dirpath, f)
            if(f.find("classifier") > -1):
                result["classifier"] = path
            elif(f.find("model") > -1):
                result["model"] = path
            elif(f.find("label_encoder") > -1):
                result["label_encoder"] = path

        results[name] = result
    
    return results
        

def readModels():
    for dirpath, dnames, fnames in os.walk(config.MODELS_DIR_PATH):
        for d in dnames:
            if d == "__pycache__":
                pass
            elif d == "custom":
                customs = read_files(os.path.join(config.MODELS_DIR_PATH + f"\\{d}"))
                pass
            elif d == "default":
                defaults = read_files(os.path.join(config.MODELS_DIR_PATH + f"\\{d}"))
                pass
        break

    return customs, defaults

"""
flow custom

get_raw_data() -> rawData : pd.DataFrame
preprocess(rawData) -> prepData {function gaussian smoother}

select_feature() -> features {array of selected features}
feature_extractions(prepData, features) -> featureData

import_ai_model_from_file() -> importedAiLib
verify_structure(importedAiLib) -> importedAiLib

importedAiLib.train(featureData)
importedAiLib.save() {store to database of ai model}

take_data_sample() -> dataSample
ai_model_select() -> selectedAIModel
preprocess(dataSample) -> prepSample

selectedAIModel.predict(prepSample) -> prediction

raw_data_show(dataSample)
prediction_show(prediction)

"""

class Genose(QObject):
    data_collection_finished = pyqtSignal(int)
    data_collection_progress = pyqtSignal(int)
    predict_finished = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.aiModel = None
        self.sensorData = None
        self.predictions = []

        self.DEFAULT_AI_DICT = AI_MODEL_DICT
        self.CUSTOM_AI_DICT = {}

    def __onDataCollectionFinish(self, datas : pd.DataFrame):
        self.sensorData = datas
        self.data_collection_finished.emit(SUCCESS)

    def __onDataCollectionProgress(self, progress : int):
        self.data_collection_progress.emit(progress)

    def __onPredictFinish(self, predictions):
        print(f"predictions : {predictions}")
        self.predictions = predictions
        self.predict_finished.emit(SUCCESS)

    def loadModelModuleFromFile(self, path : str, name : str):
        ai_module = load_module(source=path, module_name=name)
            
        if(self.verifyModelModule(ai_module)):
            return ai_module
        else:
            return None
    
    def loadModelsFromFolder(self):
        customs, defaults = readModels()

        customAiDict = {}

        for customk in customs.keys():
            custom_ai_module = load_module(source=customs[customk]["classifier"], module_name=customk)
            
            if(self.verifyModelModule(custom_ai_module)):
                customAiDict[customk] = {}
                customAiDict[customk]["module"] = custom_ai_module

        self.CUSTOM_AI_DICT = customAiDict

    def verifyModelModule(self, module) -> bool:
        try:
            predictor : BaseClassifier = module.Classifier()
            
            try:
                predict = predictor.predict
            except AttributeError as e:
                # print("predict method not implemented yet")
                raise AttributeError("predict")

            try:
                train = predictor.train
            except AttributeError as e:
                # print("train method not implemented yet")
                raise AttributeError("train")
            
            try:
                save = predictor.save
            except AttributeError as e:
                # print("train method not implemented yet")
                raise AttributeError("save")
            
        except AttributeError as e:
            print(f"Python file not in correct format : undefined function {e}")
            return False
        
        return True

    def setAIModel(self, model_id : str):
        model = None

        if(model_id in self.DEFAULT_AI_DICT.keys()):
            model = self.DEFAULT_AI_DICT[model_id]["model"]()
            paths = self.DEFAULT_AI_DICT[model_id]["paths"]
            model.load(model_path= paths["model"], label_encoder_path= paths["label_encoder"])
        elif(model_id in self.CUSTOM_AI_DICT.keys()):
            modelModule = self.CUSTOM_AI_DICT[model_id]["module"]
            model : BaseClassifier = modelModule.Classifier()
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