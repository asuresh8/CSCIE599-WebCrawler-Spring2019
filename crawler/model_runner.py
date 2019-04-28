import pickle
import app

class ModelRunner:
    def __init__(self, filepath):
        self.model_file = filepath

    def run(self, text):
        app.context.logger.info("start running the model")
        try:
            self.construct_model()
            return self.make_prediction(text)
        except Exception as e:
            app.context.logger.info("exception thrown while running model %s", str(e))

    def construct_model(self):
        self.new_vectorizer = pickle.load(open("vectorizer.pickle", "rb"))
        self.model = pickle.load(open(self.model_file, "rb"))


    def make_prediction(text):
        vectors = self.new_vectorizer.transform([text])
        prediction = 0 #self.model.predict(vectors)
        return prediction[0]
