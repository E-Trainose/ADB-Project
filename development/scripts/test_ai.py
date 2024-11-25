from development.devGUI.classifier import NNClassifier, SVMClassifier, RFClassifier
import pandas as pd
import config

if __name__ == '__main__':
    loaded_data = pd.read_csv(config.WORKING_DIR_PATH + "/data/Processed_Sensor_Data.csv")

    nncls = NNClassifier()
    nncls.load(
        model_path=config.NN_MODEL_PATH,
        label_encoder_path=config.NN_LABEL_ENCODER_PATH
    )

    nn_predicted_labels = nncls.predict(data=loaded_data)

    print(f"NN Predicted labels : {nn_predicted_labels}")

    svm = SVMClassifier()
    svm.load(
        model_path=config.SVM_MODEL_PATH,
        label_encoder_path=config.SVM_LABEL_ENCODER_PATH
    )

    svm_predicted_labels = svm.predict(data=loaded_data)
    
    print(f"SVM Predicted labels : {svm_predicted_labels}")

    rf = RFClassifier()
    rf.load(
        model_path = config.RF_MODEL_PATH,
        label_encoder_path = config.RF_LABEL_ENCODER_PATH
    )

    rf_predicted_labels = rf.predict(data=loaded_data)

    print(f"RF Predicted labels : {rf_predicted_labels}")

    # data = pd.DataFrame()
    # # Append predictions to the dataset
    # data['PREDICTED_LABEL'] = predicted_labels
    #
    # # Save the predictions to a new file
    # output_file = './svm_prediction_result.csv'
    # data.to_csv(output_file, index=False)
    #
    # print(f"Predictions saved to '{output_file}'")