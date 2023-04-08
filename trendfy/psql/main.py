from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Union

import numpy as np
import pandas as pd
import psycopg2 as psql  # type: ignore
from psycopg2.extensions import register_adapter  # type: ignore
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, create_engine, select  # type: ignore
from sqlalchemy.engine import Dialect  # type: ignore
from sqlalchemy.ext.declarative import declarative_base  # type: ignore
from sqlalchemy.orm import sessionmaker  # type: ignore
from sqlalchemy.sql.schema import ForeignKey  # type: ignore

from trendfy.tools import get_dotenv, print_message


def addapt_numpy_float64(numpy_float64):
    data = numpy_float64.item()
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
    explicit = Column(Boolean)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Float)
    loudness = Column(Float)
    mode = Column(Float)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Float)

    def __repr__(self):
        return (
            f"<Tracks(id='{self.id}', "
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


def read_db(table_name: str, engine: Dialect = None) -> pd.DataFrame:
    if engine is None:
        path_db = (
            f"postgresql://{get_dotenv('user_db')}:"
            f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
            f":{get_dotenv('port_db')}/{get_dotenv('database_db')}"
        )
        engine = create_engine(path_db)
    return pd.read_sql_table(table_name, engine)


def update_db(data: pd.Series, ids: pd.Series, db_name: str, column: str):
    # db_DataFrame = read_db(db_name)
    # df_new_values = pd.DataFrame(data.append(ids, ignore_index=True))
    if db_name == "albums":
        db_class = Albums
    if db_name == "tracks":
        db_class = Tracks

    stmt = select(db_class).where(db_class.c.id in list(ids))
    print(f"{stmt = }")
    psql_query(stmt)


def write_into_db(data: pd.DataFrame, db_name: str):
    """"""
    data_local = []
    if db_name == "albums":
        db_class = Albums
        data_local = [
            db_class(
                id=data.iloc[i]["id"],
                name=data.iloc[i]["name"],
                artist=data.iloc[i]["artist"],
                style=data.iloc[i]["style"],
                release_date=datetime.strptime(data.iloc[i]["release_date"], "%Y-%m-%d")
                if data.iloc[i]["release_date"].count("-") == 2
                else datetime.strftime(
                    datetime.strptime(data.iloc[i]["release_date"], "%Y-%m"),
                    "%Y-%m-%d",
                )
                if "-" in data.iloc[i]["release_date"]
                else datetime.strftime(
                    datetime.strptime(data.iloc[i]["release_date"], "%Y"),
                    "%Y-%m-%d",
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
                popularity=int(data.iloc[i]["popularity"]),
                duration_ms=int(data.iloc[i]["duration_ms"]),
                explicit=data.iloc[i]["explicit"].astype("bool"),
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
            if not data.iloc[i].isna()[0]
        ]

    commit_db(db_class, data_local)
    print_message(
        "Success",
        f"{len(data_local)} entries saved into '{db_name}' database.",
        "s",
    )


def commit_db(table: Any, data: List[Union[Tracks, Albums]]):
    """Commit new tracks or albums into db trendfy

    Keyword arguments:
    table -- to add into.
    data -- DataFrame to insert into.
    """
    path_db = (
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}"
    )
    engine = create_engine(path_db)

    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        # Request the ids from albums in database
        db_ids_set = set([])
        db_ids = session.query(table.id).all()
        for (db_id,) in db_ids:
            db_ids_set.add(db_id)

        # Get local ids from collection
        local_ids = set([])
        for value in data:
            local_ids.add(value.id)

        # Add non duplicates to database
        ids_to_add = local_ids - db_ids_set
        if ids_to_add:
            error_in_commit = True
            while error_in_commit:
                try:
                    session.add_all([value for value in data if value.id in ids_to_add])
                    session.commit()
                    error_in_commit = False
                except Exception as e:
                    if "DETAIL:  Key (id)" in e.args[0]:
                        id_err = e.args[0].split("DETAIL:  Key (id)=(")[1].split(") already exists")[0]
                        ids_to_add = ids_to_add - set([id_err])
                        session.rollback()
                        print_message("Removing duplicate...", f"Id: {id_err}")
                    elif "DETAIL:  Key (album_id)" in e.args[0]:
                        album_id_err = (
                            e.args[0].split("DETAIL:  Key (album_id)=(")[1].split(") is not present in table")[0]
                        )
                        tracks_to_remove = [value.id for value in data if value.album_id == album_id_err]
                        ids_to_add = ids_to_add - set(tracks_to_remove)
                        session.rollback()
                        print_message(
                            "Removing tracks of missing album...",
                            f"Album Id: {album_id_err}",
                        )


def psql_connect(func: Any) -> Any:
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
                with conn.cursor() as cursor:
                    res = func(*args, **kwargs, cursor=cursor)

            return res

        except Exception as e:
            print_message("Database", "Error!", "e")
            print(e)

        finally:
            conn.close()
            print_message("Database", "Disconnected!", "s")

    return wrapper


@psql_connect
def psql_query(cursor: Any = None):
    """Query the DB."""
    while True:
        query = input("Query: \n>>> ")

        if query == "":
            query = "select * from person"
            type_query = "select"
        else:
            query_command = query.split()[0]
            if "select" in query_command:
                type_query = "select"
            elif "delete" in query_command:
                type_query = "delete"
            else:
                type_query = "select"
        cursor.execute(query)

        if type_query == "select":
            rows = cursor.fetchall()
            for row in rows:
                print(f"{row}")
            print(f"\n{len(rows)} matches.")


if __name__ == "__main__":
    psql_query()
