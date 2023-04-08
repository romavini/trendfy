import sys
from typing import List

from trendfy.psql.main import write_into_db
from trendfy.spotify_colect import Colect
from trendfy.tools import print_message


class Trendfy(Colect):
    def __init__(
        self,
        max_repertoire: int,
        styles: List[str],
        years: range,
    ):
        super().__init__(
            max_repertoire,
            styles,
            years,
        )

        self.styles = styles
        self.years = years

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

        write_into_db(df_repertoire, "albums")

        print_message(
            "Success",
            f"{len(df_repertoire)} albums collected. " f"Expected {df_repertoire['n_of_tracks'].sum()} tracks.",
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
