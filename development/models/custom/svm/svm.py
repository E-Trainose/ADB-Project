from development.devGUI.classifier import BaseClassifier, BasePreproccessor

class SpecialPreprocessor(BasePreproccessor):
    def __init__(self):
        super().__init__()
    
    def preproccess(self, datas):
        return datas
    
class Classifier(BaseClassifier):
    def __init__(self):
        super().__init__()

        self.preprocessor = SpecialPreprocessor()

    def predict(self, datas):
        processed = self.preprocessor.preproccess(datas)
        print("Custom SVM Predictor")
        return [0, 1]