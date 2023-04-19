import pandas as pd

from trendfy.analyse import Analyse, analyse


def test_Analyse_init():
    analyse_obj = Analyse()
    assert isinstance(analyse_obj.tracks, pd.DataFrame)
    assert isinstance(analyse_obj.albums, pd.DataFrame)


def test_Analyse_status(capsys):
    analyse_obj = Analyse()
    analyse_obj.status()
    captured = capsys.readouterr()
    assert "self.tracks = " in captured.out
    assert "self.tracks.shape = " in captured.out
    assert "self.tracks.columns = " in captured.out
    assert "self.tracks.dtypes = " in captured.out
    assert "self.albums = " in captured.out
    assert "self.albums.shape = " in captured.out
    assert "self.albums.columns = " in captured.out
    assert "self.albums.dtypes = " in captured.out


def test_analyse():
    assert analyse() is None
