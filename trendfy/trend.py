import sys
from typing import List, Optional

import pandas as pd

from trendfy.errors import EmptyData
from trendfy.psql.main import read_db, write_into_db
from trendfy.spotify_colect import Colect
from trendfy.tools import print_message


class Trendfy(Colect):
    def __init__(
        self,
        max_repertoire: Optional[int] = None,
        styles: Optional[List[str]] = None,
        years: Optional[range] = None,
    ):
        self.styles = styles  # type: ignore
        self.years = years  # type: ignore

        super().__init__(
            max_repertoire,
            self.styles,
            self.years,
        )

    def colector_runner(
        self,
    ):
        """Collector logic"""
        all_styles, _ = self.get_styles()

        self.styles = all_styles if self.styles is None else self.styles

        if any((error_style := style) not in all_styles for style in self.styles):
            raise ValueError(f"{error_style} not in style list of Spotify")

        df_repertoire = self.collect_n_save_repertoire()

        self.collect_n_save_tracks(df_repertoire)

    def collect_n_save_repertoire(self):
        df_repertoire = self.iter_search_repertoires()

        if len(df_repertoire) == 0:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()
        try:
            write_into_db(df_repertoire, "albums")

            print_message(
                "Success",
                f"{len(df_repertoire)} albums collected. " f"Expected {df_repertoire['n_of_tracks'].sum()} tracks.",
                "s",
            )
        except EmptyData:
            print_message(
                "Info",
                f"{len(df_repertoire)} albums already in DB. "
                f"Checking expected {df_repertoire['n_of_tracks'].sum()} tracks.",
                "s",
            )

        return df_repertoire

    def collect_n_save_tracks(self, df_repertoire):
        df_track = self.search_tracks_from_repertoire(df_repertoire)

        if len(df_track) == 0:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()

        write_into_db(df_track, "tracks")

    def repair(self):
        albums_db = read_db("albums")
        print_message("Success", f"{albums_db.shape[0]} albums in DB", "s")
        tracks_db = read_db("tracks")
        print_message("Success", f"{tracks_db.shape[0]} tracks in DB", "s")
        seek_tracks = self.search_tracks_from_repertoire(albums_db)
        tracks_to_add = self.get_tracks_to_add(tracks_db, seek_tracks)
        tracks_to_add = tracks_to_add.drop(columns=["album_popularity"])
        if tracks_to_add.shape[0]:
            print_message("Success", f"{tracks_to_add.shape[0]} tracks to be added in DB", "s")
            write_into_db(tracks_to_add, "tracks")
        else:
            print_message("Success", "No tracks to be added in DB", "s")

    @staticmethod
    def get_tracks_to_add(tracks_db: pd.DataFrame, tracks_to_add: pd.DataFrame) -> pd.DataFrame:
        ids_to_add = set(tracks_to_add.id) - set(tracks_db.id)

        return tracks_to_add.loc[tracks_to_add.id.isin(ids_to_add)].copy()
