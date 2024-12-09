from classifier import BaseClassifier

class Classifier(BaseClassifier):
    def predict(self, datas):
        print("Custom SVM EXT Predictor")
        return [0, 1]
    def train(self, datas):
        return [1]