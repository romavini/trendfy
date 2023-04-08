import pandas as pd
from sklearn.base import ClassifierMixin  # type: ignore

from trendfy.model import ModelSklearnTrendfy


class TrendifyAnalyse(ModelSklearnTrendfy):
    def __init__(self, model: ClassifierMixin):
        super().__init__()
        self.df = pd.read_csv("/content/df.csv").drop(columns=["Unnamed: 0"])

        self.model = model

    def fit(self, x_train: pd.DataFrame, y_train: pd.Series):
        self.model.fit(x_train, y_train)

    def predict(self, x_test: pd.DataFrame):
        return self.model.predict(x_test)
