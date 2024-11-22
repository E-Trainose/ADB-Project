from ai_start import NNClassifier, SVMClassifier, RFClassifier
import pandas as pd

loaded_data = pd.read_csv("./data/Processed_Sensor_Data.csv")

# nncls = NNClassifier()
# nncls.load(
#     model_path="./model/nn/nn_model.pth",
#     label_encoder_path="./model/nn/label_encoder_nn.pkl"
# )
#
# nn_predicted_labels = nncls.predict(data=loaded_data)
#
# svm = SVMClassifier()
# svm.load(
#     model_path="./model/svm/svm_model.pkl",
#     label_encoder_path="./model/svm/label_encoder_svm.pkl"
# )
#
# svm_predicted_labels = svm.predict(data=loaded_data)



# data = pd.DataFrame()
# # Append predictions to the dataset
# data['PREDICTED_LABEL'] = predicted_labels
#
# # Save the predictions to a new file
# output_file = './svm_prediction_result.csv'
# data.to_csv(output_file, index=False)
#
# print(f"Predictions saved to '{output_file}'")
nncls = NNClassifier()
nncls.load(
    model_path="./model/nn/nn_model.pth",
    label_encoder_path="./model/nn/label_encoder_nn.pkl"
)

nn_predicted_labels = nncls.predict(data=loaded_data)

svm = SVMClassifier()
svm.load(
    model_path="./model/svm/svm_model.pkl",
    label_encoder_path="./model/svm/label_encoder_svm.pkl"
)

svm_predicted_labels = svm.predict(data=loaded_data)

rf = RFClassifier()
rf.load(
    model_path = "./model/rf/random_forest_model.pkl",
    label_encoder_path = "./model/rf/label_encoder_rf.pkl"
)

rf_predicted_labels = rf.predict(data=loaded_data)