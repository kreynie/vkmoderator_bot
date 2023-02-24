from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pandas as pd
import joblib


class BadWordsDetector:
    def __init__(
        self,
        model_file: str = "wordsdetector/trained/model.joblib",
        csv_file: str = "wordsdetector/dataset/words.csv",
    ):
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
        self.csv_file = csv_file
        self.model_file = model_file

    async def train(self) -> None:
        data = pd.read_csv(self.csv_file, quotechar="`", engine="python")
        X = data["comment"].values
        y = data["toxic"].values
        self.model.fit(X, y)
        await self.save()

    async def predict(self, comment) -> list:
        return self.model.predict((comment,))[0]

    async def save(self) -> None:
        joblib.dump(self.model, self.model_file)

    async def add_text_data(self, comment, toxic) -> None:
        with open(self.csv_file, "a", encoding="utf-8") as f:
            f.write("`{}`,{}\n".format(comment, float(toxic)))
