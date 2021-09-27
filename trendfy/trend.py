import sys
from typing import List, Union
from trendfy.psql.main import read_db, update_db, write_into_db
from trendfy.spotify_colect import Colect
from trendfy.helpers import print_message


class Trendfy:
    def __init__(
        self,
        overwrite: bool,
        max_repertoire: int,
        max_ids_request: int,
        start_from: str,
    ):
        self.colect = Colect(
            overwrite=overwrite,
            max_repertoire=max_repertoire,
            max_ids_request=max_ids_request,
        )
        self.start_from = start_from

    def colector_runner(
        self,
        styles: Union[List[str], None],
        years: range,
        repertoire_type: str = "album",
    ):
        """"""
        if self.start_from == "a":
            if styles is None:
                styles = self.colect.get_styles()

            df_repertoire = self.colect.search_repertoires(styles, years, repertoire_type)

            if len(df_repertoire) == 0:
                print_message(
                    "Success",
                    "No new data to be saved.",
                    "s",
                )
                sys.exit()

            write_into_db(df_repertoire, "albums")

        elif self.start_from == "t":
            df_repertoire = read_db("albums")

        print_message(
            "Success",
            f"{len(df_repertoire)} {repertoire_type} collected. "
            f"Expected {df_repertoire['n_of_tracks'].sum()} tracks.",
            "s",
        )

        df_track = self.colect.search_tracks_from_repertoire(
            df_repertoire, repertoire_type
        )

        if len(df_track) == 0:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()
        else:
            write_into_db(df_track, "tracks")

        update_db(
            df_track["album_popularity"],
            df_track["id"],
            "albums",
            "popularity",
        )
