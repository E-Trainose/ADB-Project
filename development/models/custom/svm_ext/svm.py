from development.devGUI.classifier import BaseClassifier

class Classifier(BaseClassifier):
    def predict(self, datas):
        print("Custom SVM EXT Predictor")
        return [0, 1]