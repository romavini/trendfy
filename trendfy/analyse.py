from trendfy.psql.main import read_db


class Analyse:
    def __init__(self):
        self.tracks = read_db("tracks")
        self.albums = read_db("albums")

    def status(self):
        print(f"{self.tracks = }")
        print(f"{self.tracks.shape = }")
        print(f"{self.tracks.columns = }")
        print(f"{self.tracks.dtypes = }")
        print(f"{self.albums = }")
        print(f"{self.albums.shape = }")
        print(f"{self.albums.columns = }")
        print(f"{self.albums.dtypes = }")


def analyse():
    analyse = Analyse()
    analyse.status()
