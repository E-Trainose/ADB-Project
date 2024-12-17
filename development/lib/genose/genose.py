import sys, os, platform, time, traceback
from lib.genose.classifier import BaseClassifier, NNClassifier, SVMClassifier, RFClassifier, PredictionThread
from lib.communication.data_collector import DataCollectionThread, DataCollector
from lib.communication.communication import Communication
import config
import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QRunnable, QThreadPool
import importlib.util
import sys
import string
import secrets
import serial.tools.list_ports
from serial import Serial

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
    1 : "ALKOHOL",
    10 : "KOPI",
    100 : "TEH"
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

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)

class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit("result")  # Done

class FindPortWorker(QRunnable, QObject):
    def __init__(self):
        super().__init__()

        self.signal = WorkerSignals()
    
    def run(self):
        selectedPort = ""
        ports = serial.tools.list_ports.comports()
        cur = 0
        ports_ln = len(ports)

        for port in ports:
            try:
                self.signal.progress.emit(int((cur / ports_ln) * 100))
                cur += 1

                portname = port.device

                system = platform.system()
                if(system == "Linux"):
                    portname = portname

                print(f"opening port {portname}")
                ser = Serial(port=portname, baudrate=9600, timeout=1, write_timeout=1)
                ser.flush()

                time.sleep(2)
                
                sent = 0
                sent += ser.write(Communication.toByte(Communication.Command.INIT, 0))
                sent += ser.write(b'\n')

                recv = ser.read_until(b'\n')

                print(f"received : {recv}")

                parsed = Communication.toNumber(recv[0:8])
                cmd = parsed[0]
                val = parsed[1]
                
                if(cmd == Communication.Command.OK):
                    selectedPort = portname
                    break
                
            except Exception as e:
                print(e)
            
            finally:
                ser.close()

        self.signal.finished.emit(selectedPort)

class PreprocessWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)
    
    def setDatas(self, datas : pd.DataFrame):
        self.datas = datas

    def run(self):
        # preprocess
        return self.datas

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
    genose_port_search_finished = pyqtSignal(str)
    genose_port_search_progress = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.aiModel = None
        self.sensorData = None
        self.predictions = []

        self.DEFAULT_AI_DICT = AI_MODEL_DICT
        self.CUSTOM_AI_DICT = {}

        self.threadpool = QThreadPool()

    def __onDataCollectionFinish(self, datas : pd.DataFrame):
        self.sensorData = datas
        self.data_collection_finished.emit(SUCCESS)

    def __onDataCollectionProgress(self, progress : int):
        self.data_collection_progress.emit(progress)

    def __onPredictFinish(self, predictions):
        print(f"predictions : {predictions}")
        self.predictions = predictions
        self.predict_finished.emit(SUCCESS)

    def findGenosePort(self):
        self.findportworker = FindPortWorker()
        self.findportworker.signal.progress.connect(lambda x : self.genose_port_search_progress.emit(x))
        self.findportworker.signal.finished.connect(lambda x : self.genose_port_search_finished.emit(x))
        
        self.threadpool.start(self.findportworker)


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

    def setInhaleFlushTimerSetting(self, port, inhale, flush):
        dataCollector = DataCollector(port=port)
        dataCollector.initialize()
        dataCollector.sendSetInhale(inhale)
        dataCollector.sendSetFlush(flush)
        dataCollector.deinitialize()

    def extractFeatures(self, datas : pd.DataFrame, features):
        return datas

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

    def startPreprocess(self):
        self.prepWorker = PreprocessWorker()
        self.prepThread = QThread()

        self.prepWorker.moveToThread(self.prepThread)

        self.prepThread.started.connect(self.prepWorker.run)
        # self.prepWorker.progress.connect(lambda val: self.genose_port_search_progress.emit(val))
        # self.prepWorker.finished.connect(lambda port: self.genose_port_search_finished.emit(port))
        self.prepWorker.finished.connect(self.prepThread.quit)
        
        # self.prepWorker.port_search_finished.connect(self.prepWorker.deleteLater)
        self.prepThread.finished.connect(self.prepThread.deleteLater)

        self.prepThread.start()

    def __startTraining(self, aiModule, features, label, progress_callback = None):
        try:
            classifier : BaseClassifier = aiModule.Classifier()

            datas = self.sensorData

            datas = self.extractFeatures(datas, features)
            
            result = classifier.train(self.sensorData)

            print(f"Akurasi : {result}")

            # return classifier
    
        except Exception as e:
            print(e)
        
    def startTraining(self, aiModule, features):
        worker = Worker(self.__startTraining, aiModule, features)
        
        self.threadpool.start(worker)