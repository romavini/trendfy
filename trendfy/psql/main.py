from trendfy.helpers import get_dotenv, print_message
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable
import pandas as pd
import psycopg2 as psql
from psycopg2.extensions import register_adapter, AsIs
from sqlalchemy import (
    select,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import numpy as np


def addapt_numpy_float64(numpy_float64):
    print(f"{numpy_float64 = }")
    print(f"{type(numpy_float64) = }")
    data = numpy_float64.item()
    print(f"{data = }")
    print(f"{type(data) = }")
    return data


Base = declarative_base()
register_adapter(np.int64, addapt_numpy_float64)


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
            f"n_of_tracks='{self.n_of_tracks}')>"
        )


@dataclass
class Tracks(Base):  # type: ignore
    __tablename__ = "tracks"
    id = Column(String, primary_key=True)
    name = Column(String)
    album_id = Column(String, ForeignKey("albums.id"))
    popularity = Column(Integer)
    duration_ms = Column(Integer)
    explicit = Column(Integer)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Float)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Integer)

    def __repr__(self):
        return (
            f"<Album(id='{self.id}', "
            f"name='{self.name}', "
            f"album_id='{self.album_id}', "
            f"popularity='{self.popularity}', "
            f"duration_ms='{self.duration_ms}', "
            f"explicit='{self.explicit}', "
            f"danceability='{self.danceability}', "
            f"energy='{self.energy}', "
            f"key='{self.key}', "
            f"loudness='{self.loudness}', "
            f"mode='{self.mode}', "
            f"speechiness='{self.speechiness}', "
            f"acousticness='{self.acousticness}', "
            f"instrumentalness='{self.instrumentalness}', "
            f"liveness='{self.liveness}', "
            f"valence='{self.valence}', "
            f"tempo='{self.tempo}', "
            f"time_signature='{self.time_signature}')>"
        )


def read_db(db_class: str) -> pd.DataFrame:
    engine = create_engine(
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}",
    )
    return pd.read_sql_table(db_class, engine)


def update_db(data: pd.Series, ids: pd.Series, db_name: str, column):
    # db_DataFrame = read_db(db_name)
    # df_new_values = pd.DataFrame(data.append(ids, ignore_index=True))

    stmt = select(Albums).where(Albums.c.id in list(ids))
    print(f"{stmt = }")
    psql_query(stmt, "select")


def write_into_db(data: pd.DataFrame, db_name: str):
    """"""
    if db_name == "albums":
        db_class = Albums
        data_local = [
            db_class(
                id=data.iloc[i]["id"],
                name=data.iloc[i]["name"],
                artist=data.iloc[i]["artist"],
                style=data.iloc[i]["style"],
                release_date=data.iloc[i]["release_date"]
                if "-" in data.iloc[i]["release_date"]
                else datetime.strftime(
                    datetime.strptime(data.iloc[i]["release_date"], "%Y"), "%Y/%m/%d"
                ),
                popularity=0,
                n_of_tracks=int(data.iloc[i]["n_of_tracks"]),
            )
            for i in range(len(data))
        ]
    elif db_name == "tracks":
        db_class = Tracks
        data_local = [
            db_class(
                id=data.iloc[i]["id"],
                name=data.iloc[i]["name"],
                album_id=data.iloc[i]["album_id"],
                popularity=data.iloc[i]["popularity"],
                duration_ms=data.iloc[i]["duration_ms"],
                explicit=data.iloc[i]["explicit"],
                danceability=data.iloc[i]["danceability"],
                energy=data.iloc[i]["energy"],
                key=data.iloc[i]["key"],
                loudness=data.iloc[i]["loudness"],
                mode=data.iloc[i]["mode"],
                speechiness=data.iloc[i]["speechiness"],
                acousticness=data.iloc[i]["acousticness"],
                instrumentalness=data.iloc[i]["instrumentalness"],
                liveness=data.iloc[i]["liveness"],
                valence=data.iloc[i]["valence"],
                tempo=data.iloc[i]["tempo"],
                time_signature=data.iloc[i]["time_signature"],
            )
            for i in range(len(data))
        ]

    commit_db(db_class, data_local)
    print_message("Success", f"{len(data)} entries saved into database.", "s")


def commit_db(table: Any, data: pd.DataFrame):
    """Commit new tracks or albums into db trendfy

    Keyword arguments:
    table -- to add into.
    data -- DataFrame to insert into.
    """
    engine = create_engine(
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}",
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


def psql_connect(func: Callable) -> Callable:
    """Connect to DB."""

    def wrapper(*args, **kwargs) -> Any:
        try:
            with psql.connect(
                user=get_dotenv("user_db"),
                password=get_dotenv("password_db"),
                host=get_dotenv("host_db"),
                port=get_dotenv("port_db"),
                database=get_dotenv("database_db"),
            ) as conn:
                print_message("Database", "Connected!", "s")
                with conn.cursor() as c:
                    res = func(*args, **kwargs, c=c)

            return res

        except Exception as e:
            print_message("Database", "Error!", "e")
            print(e)

        finally:
            conn.close()
            print_message("Database", "Disconnected!", "s")

    return wrapper


@psql_connect
def psql_query(q: str, type_q: str, c: Any):
    """Quary the DB."""
    c.execute(q)

    if type_q == "select":
        rows = c.fetchall()
        for row in rows:
            print(f"{row}")


if __name__ == "__main__":
    q = input("Query: \n>>> ")

    if q == "":
        q = "select * from person"
        type_q = "select"
    else:
        q_comp = q.split()[0]
        if "select" in q_comp:
            type_q = "select"
        elif "delete" in q_comp:
            type_q = "delete"
        else:
            type_q = "select"

    psql_query(q, type_q)
