from genose import Genose

genose = Genose()

genose.loadModelsFromFolder()
print(genose.CUSTOM_AI_DICT)
# genose.setAIModel("NN")

print(genose.aiModel)
