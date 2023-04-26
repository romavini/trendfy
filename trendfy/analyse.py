from trendfy.model import ModelSklearnTrendfy
from trendfy.psql.main import read_db


class Analyse:
    def __init__(self):
        self.model = None
        self.tracks = read_db("tracks")
        self.albums = read_db("albums")
        print(self.tracks.columns)

    def status(self):
        print(f"{self.tracks = }")
        print(f"{self.tracks.shape = }")
        print(f"{self.tracks.columns = }")
        print(f"{self.tracks.dtypes = }")
        print(f"{self.albums = }")
        print(f"{self.albums.shape = }")
        print(f"{self.albums.columns = }")
        print(f"{self.albums.dtypes = }")

    def make_sets(self):
        self.model = ModelSklearnTrendfy()
        self.model.select_training_data(self.tracks)


def analyse():
    analyse = Analyse()
    analyse.status()
    analyse.status()
