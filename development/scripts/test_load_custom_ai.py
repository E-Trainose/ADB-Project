import importlib.util
import sys
import string
import secrets

from development.devGUI.classifier import BaseClassifier

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

MODEL_PATH = ""
MODEL_NAME = ""

print(sys.argv)

if(sys.argv[1] == "svm"):
    MODEL_PATH = "./model/custom/svm/svm.py"
    MODEL_NAME = "custom_svm"
else:
    MODEL_PATH = "./model/custom/svm_ext/svm.py"
    MODEL_NAME = "custom_svm_ext"

custom_ai_module = load_module(source=MODEL_PATH, module_name=MODEL_NAME)
predictor : BaseClassifier = custom_ai_module.Classifier()
prediction = predictor.predict([0, 1, 2])

print(prediction)