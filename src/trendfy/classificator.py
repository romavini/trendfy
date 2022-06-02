import pandas as pd
from trendfy.model import ModelSklearnTrendfy


class TrendifyAnalyse(ModelSklearnTrendfy):
    def __init__(self, model):
        self.df = pd.read_csv("/content/df.csv").drop(columns=["Unnamed: 0"])

        self.model = model

    def fit(self, X, y):
        self.model.fit(X, y)

    def predict(self, X):
        return self.model.predict(X)
