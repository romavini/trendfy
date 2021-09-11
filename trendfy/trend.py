import sys
from typing import List, Union
from trendfy.psql.main import read_db, write_into_db
from trendfy.spotify_colect import Colect
from trendfy.helpers import print_message


class Trendfy:
    def __init__(
        self,
        overwrite: bool = False,
        max_repertoire: int = 20,
        max_ids_request: int = 50,
        start_from: str = "b",
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
        if self.start_from == "b":
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

        if self.start_from in ["b", "t"]:
            print_message(
                "Success",
                f"{len(df_repertoire)} {repertoire_type} collected. "
                f"Expected {df_repertoire['n_of_tracks'].sum()} tracks.",
                "s",
            )
            # TODO: Fix the colect of tracks
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

            # TODO: Write int database
            self.colect.write_json(
                df_track,
                data_type="df",
                filename="df_tracks",
                overwrite=self.colect.overwrite,
            )

        if self.start_from == "d":
            df_track = read_json_to_df("df_tracks")

        old_df = read_json_to_df("df_track_details")
        df_track = self.colect.check_existent_tracks(df_track, old_df)

        # TODO: Unite the details to the search of tracks
        tracks_details = self.colect.search_track_details(df_track)

        if len(tracks_details) == 0:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )

        write_into_db(tracks_details, "tracks")
