# from genose import Genose
from lib.communication.communication import Communication

# genose = Genose()

# genose.loadModelsFromFolder()
# print(genose.CUSTOM_AI_DICT)
# # genose.setAIModel("NN")

# print(genose.aiModel)


to_send = Communication.toByte(Communication.Command.ERR_INIT, 0)

print(to_send)

received = Communication.toNumber(to_send[0:8])

print(received)