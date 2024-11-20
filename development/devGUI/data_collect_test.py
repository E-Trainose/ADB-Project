from data_collector import DataCollector

dCol = DataCollector(port='COM2')
dCol.collect(amount=10)
dCol.save('kontoltake')