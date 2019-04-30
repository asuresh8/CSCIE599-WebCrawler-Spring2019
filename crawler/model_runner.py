import pickle
from crawl_global import CrawlGlobal
from sklearn.model_selection import *
from sklearn.feature_extraction.text import *

class ModelRunner:
    def __init__(self, filepath):
        self.model_file = filepath

    def run(self, text):
        CrawlGlobal.context().logger.info("start running the model")
        try:
            self.construct_model()
            return self.make_prediction(text)
        except Exception as e:
            CrawlGlobal.context().logger.info("exception thrown while running model %s", str(e))

    def construct_model(self):
        try:
            CrawlGlobal.context().logger.info("deserailizing the model")
            self.new_vectorizer = pickle.load(open("vectorizer.pickle", "rb"))
            self.model = pickle.load(open(self.model_file, "rb"))
        except Exception as e:
            CrawlGlobal.context().logger.info("error in deserializing: %s" , str(e))

    def make_prediction(self,text):
        try:
            CrawlGlobal.context().logger.info("transforming and predicting")
            vectors = self.new_vectorizer.transform([text])
            prediction = self.model.predict(vectors)
            CrawlGlobal.context().logger.info("model predicted: %d", prediction[0])
            return prediction[0]
        except Exception as e:
            CrawlGlobal.context().logger.info("error in predicting: %s", str(e))
            return -1
