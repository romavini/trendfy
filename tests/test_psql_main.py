import pandas as pd

from trendfy.psql.main import read_db


def test_read_db(generate_engine):
    df = read_db("albums", generate_engine)
    assert type(df) == pd.DataFrame
