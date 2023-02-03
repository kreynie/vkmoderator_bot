from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib


class BadWordsDetector:
    def __init__(self, model_file="wordsdetector/trained/model.joblib"):
        if model_file:
            self.model = joblib.load(model_file)
        else:
            self.model = Pipeline(
                [
                    ("vectorizer", CountVectorizer()),
                    ("transformer", TfidfTransformer()),
                    ("classifier", LogisticRegression()),
                ]
            )

    async def train(self, csv_file):
        data = pd.read_csv(csv_file)
        X = data["comment"].values
        y = data["toxic"].values
        self.model.fit(X, y)

    async def predict(self, comments):
        return self.model.predict(comments)

    async def save(self, file_name):
        joblib.dump(self.model, file_name)

    async def add_text_data(self, comment, toxic, csv_file="wordsdetector/dataset/words.csv"):
        with open(csv_file, "a", encoding="utf-8") as f:
            f.write('\n"{}\n",{}'.format(comment, float(toxic)))
