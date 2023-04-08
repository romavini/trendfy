# %%
from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from sqlalchemy import Column, DateTime, Float, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ForeignKey

from trendfy.helpers import get_dotenv, read_json_to_df

# %%
df = read_json_to_df("../../df_repertoire_album")


# %%
Base = declarative_base()


@dataclass
class Albums(Base):  # type: ignore
    __tablename__ = "albums"
    id = Column(String, primary_key=True)
    name = Column(String)
    artist = Column(String)
    style = Column(String)
    release_date = Column(DateTime)
    popularity = Column(Integer)
    n_of_tracks = Column(Integer)

    def __repr__(self):
        return (
            f"<Album(id='{self.id}', "
            f"name='{self.name}', "
            f"artist='{self.artist}', "
            f"style='{self.style}', "
            f"release_date='{self.release_date}', "
            f"popularity='{self.popularity}', "
            f"total_tracks='{self.n_of_tracks}')>"
        )


@dataclass
class Tracks(Base):  # type: ignore
    __tablename__ = "tracks"
    id = Column(String, primary_key=True)
    name = Column(String)
    album_id = Column(String, ForeignKey("albums.id"))
    duration_ms = Column(Integer)
    explicity = Column(Integer)
    energy = Column(Float)
    key = Column(Integer)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liviness = Column(Float)
    valence = Column(Float)
    tempo = Column(Integer)
    time_signature = Column(Integer)

    def __repr__(self):
        return (
            f"<Album(id='{self.id}', "
            f"name='{self.name}', "
            f"album_id='{self.album_id}', "
            f"duration_ms='{self.duration_ms}', "
            f"explicity='{self.explicity}', "
            f"energy='{self.energy}', "
            f"key='{self.key}', "
            f"loudness='{self.loudness}', "
            f"mode='{self.mode}', "
            f"speechiness='{self.speechiness}', "
            f"acousticness='{self.acousticness}', "
            f"instrumentalness='{self.instrumentalness}', "
            f"liviness='{self.liviness}', "
            f"valence='{self.valence}', "
            f"tempo='{self.tempo}', "
            f"time_signature='{self.time_signature}')>"
        )


# %% Create albums classes
albums = [
    Albums(
        id=df.iloc[i]["id"],
        name=df.iloc[i]["name"],
        artist="to_replace",
        style=df.iloc[i]["style"],
        release_date=df.iloc[i]["release_date"]
        if "-" in df.iloc[i]["release_date"]
        else datetime.strftime(datetime.strptime(df.iloc[i]["release_date"], "%Y"), "%Y/%m/%d"),
        popularity=0,
        n_of_tracks=int(df.iloc[i]["total_tracks"]),
    )
    for i in range(100)
]


# %%
# Read df from db
def read_db(db_class):
    engine = create_engine(
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}",
        echo=True,
    )
    return pd.read_sql_table(db_class, engine)


db_r = read_db("albums")

# %%


# %%
def commit_db(table, data):
    """Commit new tracks or albums into db trendfy

    Keyword arguments:
    table -- to add into
    data --
    """
    engine = create_engine(
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}",
        echo=True,
    )

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Request the ids from albums in database
        db_ids_set = set()
        db_ids = session.query(table.id).all()
        for (db_id,) in db_ids:
            db_ids_set.add(db_id)

        # Get local ids from collection
        local_ids = set()
        for value in data:
            local_ids.add(value.id)

        # Add non duplicates to database
        ids_to_add = local_ids - db_ids_set
        if ids_to_add:
            session.add_all([value for value in data if value.id in ids_to_add])
            session.commit()


commit_db(Albums, albums)

# %%
# Drop it
# Base.metadata.drop_all(engine)
