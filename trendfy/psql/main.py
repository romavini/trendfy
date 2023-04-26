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

from trendfy.errors import EmptyData, FailToCommit  # type: ignore
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
    release_date = Column(DateTime, ForeignKey("albums.release_date"))
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
            f"release_date='{self.release_date}', "
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
    if db_name == "albums":
        db_class = Albums
    if db_name == "tracks":
        db_class = Tracks

    stmt = select(db_class).where(db_class.c.id in list(ids))
    print(f"{stmt = }")
    psql_query(stmt)


def write_into_db(data: pd.DataFrame, db_name: str):
    """Write data into Database"""
    data_local, db_class = structure_album(data) if db_name == "albums" else structure_track(data)
    commit_db(db_class, data_local)
    print_message(
        "Success",
        f"{len(data_local)} entries saved into '{db_name}' database.",
        "s",
    )


def structure_track(data):
    db_class = Tracks
    data_local = [
        db_class(
            id=str(data.iloc[i]["id"]),
            name=str(data.iloc[i]["name"]),
            album_id=str(data.iloc[i]["album_id"]),
            release_date=datetime.strptime(data.iloc[i]["release_date"], "%Y-%m-%d"),
            popularity=int(data.iloc[i]["popularity"]),
            duration_ms=int(data.iloc[i]["duration_ms"]),
            explicit=bool(data.iloc[i]["explicit"].astype("bool")),
            danceability=float(data.iloc[i]["danceability"]),
            energy=float(data.iloc[i]["energy"]),
            key=float(data.iloc[i]["key"]),
            loudness=float(data.iloc[i]["loudness"]),
            mode=float(data.iloc[i]["mode"]),
            speechiness=float(data.iloc[i]["speechiness"]),
            acousticness=float(data.iloc[i]["acousticness"]),
            instrumentalness=float(data.iloc[i]["instrumentalness"]),
            liveness=float(data.iloc[i]["liveness"]),
            valence=float(data.iloc[i]["valence"]),
            tempo=float(data.iloc[i]["tempo"]),
            time_signature=float(data.iloc[i]["time_signature"]),
        )
        for i in range(len(data))
        if not data.iloc[i].isna()[0]
    ]

    return data_local, db_class


def structure_album(data):
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
    return data_local, db_class


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
        db_ids = session.query(table.id).all()
        db_ids_set = {db_id for db_id, in db_ids}

        # Get local ids from collection
        local_ids = {value.id for value in data}

        # Add non duplicates to database
        ids_to_add = local_ids - db_ids_set

        check_data_add(ids_to_add)

        try_commit_data(data, session, ids_to_add)


def try_commit_data(data, session, ids_to_add):
    for attempt in range(1, 4):
        success, ids_to_add = attempt_commit(data, session, ids_to_add, attempt)
        if success:
            break
    else:
        raise FailToCommit


def attempt_commit(data, session, ids_to_add, attempt):
    try:
        session.add_all([value for value in data if value.id in ids_to_add])
        session.commit()
        return True, ids_to_add
    except Exception as e:
        print_message(f"Rolling Back {attempt}", f"error: {e} | Trying to commit", "e")
        ids_to_add = rollback_exception(data, session, ids_to_add, e)
        return False, ids_to_add


def check_data_add(ids_to_add):
    if not ids_to_add:
        raise EmptyData("No new data to add")


def rollback_exception(data, session, ids_to_add, e):
    if "DETAIL:  Key (id)" in e.args[0]:
        id_err = e.args[0].split("DETAIL:  Key (id)=(")[1].split(") already exists")[0]
        ids_to_add = ids_to_add - set([id_err])
        print_message("Removing duplicate...", f"Id: {id_err}")

    elif "DETAIL:  Key (album_id)" in e.args[0]:
        album_id_err = e.args[0].split("DETAIL:  Key (album_id)=(")[1].split(") is not present in table")[0]
        tracks_to_remove = [value.id for value in data if value.album_id == album_id_err]
        ids_to_add = ids_to_add - set(tracks_to_remove)
        print_message(
            "Removing tracks of missing album...",
            f"Album Id: {album_id_err}",
        )
    session.rollback()
    return ids_to_add


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
            print_message("Database", f"Error! {e}", "e")

        finally:
            conn.close()
            print_message("Database", "Disconnected!", "s")

    return wrapper


@psql_connect
def psql_query(cursor: Any = None):
    """Query the DB."""
    while True:
        query = input("Query: \n>>> ")

        query, type_query = parse_query(query)
        cursor.execute(query)

        if type_query == "select":
            show_rows(cursor)


def show_rows(cursor):
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row}")
    print(f"\n{len(rows)} matches.")


def parse_query(query):
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
    return query, type_query


if __name__ == "__main__":
    psql_query()
