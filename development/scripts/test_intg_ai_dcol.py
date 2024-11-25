from data_collector import DataCollector
from development.devGUI.classifier import NNClassifier, SVMClassifier, RFClassifier
from scipy.stats import skew, kurtosis
import pandas as pd


dCol = DataCollector(port='COM2', amount=10)
dCol.collect()
datas = dCol.getDataFrame()

print("Data Genose")
print(datas)

# Function to extract features
def extract_features(data_chunk, sensor):
    return {
        f'MEAN_{sensor}': data_chunk[sensor].mean(),
        f'MIN_{sensor}': data_chunk[sensor].min(),
        f'MAX_{sensor}': data_chunk[sensor].max(),
        f'SKEW_{sensor}': skew(data_chunk[sensor]),
        f'KURT_{sensor}': kurtosis(data_chunk[sensor])
    }

sensor_columns = ['TGS2600', 'TGS2602', 'TGS816', 'TGS813', 'MQ8','TGS2611', 'TGS2620', 'TGS822', 'MQ135', 'MQ3']

processed_data = pd.DataFrame()

# Split data into chunks of 156 rows
num_chunks = len(datas) // 156

for i in range(num_chunks):
    data_chunk = datas.iloc[i * 156:(i + 1) * 156]
    features = {}

    # Extract features for each sensor
    for sensor in sensor_columns:
        features.update(extract_features(data_chunk, sensor))

    dfeatures = pd.DataFrame(features, index=[0])

    # Append to the final DataFrame
    processed_data = pd.concat([dfeatures, processed_data])

print("Processed Data")
print(processed_data)

def classify(classifier, processed_data):
    model = None
    if(classifier == "svm"):
        model = SVMClassifier()
    elif(classifier == "rf"):
        model = RFClassifier()
    else:
        model = NNClassifier()

    predicted_labels = model.predict(data=processed_data)
    print(f"predicted labels {predicted_labels}")


classify("svm", processed_data)
classify("rf", processed_data)
classify("nn", processed_data)
