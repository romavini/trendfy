import pandas as pd
import pytest

from trendfy.analyse import Analyse, analyse


@pytest.fixture
def analyse_instance():
    return Analyse()


def test_analyse_init(analyse_instance):
    assert isinstance(analyse_instance.tracks, pd.DataFrame)
    assert isinstance(analyse_instance.albums, pd.DataFrame)


def test_analyse_status(capsys, analyse_instance):
    analyse_instance = Analyse()
    analyse_instance.status()
    captured = capsys.readouterr()
    assert "self.tracks = " in captured.out
    assert "self.tracks.shape = " in captured.out
    assert "self.tracks.columns = " in captured.out
    assert "self.tracks.dtypes = " in captured.out
    assert "self.albums = " in captured.out
    assert "self.albums.shape = " in captured.out
    assert "self.albums.columns = " in captured.out
    assert "self.albums.dtypes = " in captured.out


def test_model(analyse_instance):
    analyse_instance = Analyse()
    analyse_instance.make_sets()
    assert "X_train" in analyse_instance.model.df_dict
    assert "y_train" in analyse_instance.model.df_dict


def test_analyse():
    assert analyse() is None
