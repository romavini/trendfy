import sys
from typing import List
from trendfy.psql.main import write_into_db
from trendfy.spotify_colect import Colect
from trendfy.helpers import print_message


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
        """"""
        all_styles, err = self.get_styles()

        if err == 2:
            raise KeyboardInterrupt

        if self.styles is None:
            self.styles = all_styles
        elif any([style not in all_styles for style in self.styles]):
            raise Exception

        df_repertoire = self.search_repertoires()

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
            f"{len(df_repertoire)} albums collected. "
            f"Expected {df_repertoire['n_of_tracks'].sum()} tracks.",
            "s",
        )

        df_track = self.search_tracks_from_repertoire(df_repertoire)

        if len(df_track) == 0:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()
        else:
            write_into_db(df_track, "tracks")

        # update_db(
        #     df_track["album_popularity"],
        #     df_track["id"],
        #     "albums",
        #     "popularity",
        # )
