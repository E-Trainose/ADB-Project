from lib.communication.data_collector import DataCollector

dCol = DataCollector(port='COM2', amount=2)
dCol.collect()
datas = dCol.getDataFrame()

print(datas)