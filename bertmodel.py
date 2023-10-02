from deep_translator import GoogleTranslator
#from transformers import pipeline
import pandas as pd
def gettr(text):
    translate = GoogleTranslator(source='auto', target='en').translate(text)
    return str(translate)
def recom(text):
#     classifier = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base",
#                           return_all_scores=True)
#     return (pd.DataFrame(classifier(text)[0]).sort_values(by='score',ascending=False)).iloc[0,0]
    pass
