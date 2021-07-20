import sys
from trendfy.spotify_colect import Colect
from trendfy.helpers import print_message, read_json_to_df


class Trendfy:
    def __init__(self):
        self.colect = Colect()

    def colect_tracks(self, styles, years, repertoire_type="album"):
        df_repertoire = self.colect.search_repertoires(styles, years, repertoire_type)
        print(f"{df_repertoire['style'].unique()=}")  # debug
        print_message(
            "Success",
            f"{len(df_repertoire)} {repertoire_type} collected. "
            f"Expected {df_repertoire['total_tracks'].sum()} tracks.",
            "s",
        )
        if len(df_repertoire) != 0:
            self.colect.write_json(
                df_repertoire,
                data_type="df",
                filename=f"df_repertoire_{repertoire_type}",
                overwrite=self.colect.overwrite,
            )
        else:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()

        df_track = self.colect.search_tracks_from_repertoire(
            df_repertoire, repertoire_type
        )
        print(f"\n{df_track['style'].unique()=}")  # debug
        print_message("Success", f"{len(df_track)} tracks collected", "s")
        if len(df_track) != 0:
            self.colect.write_json(
                df_track,
                data_type="df",
                filename="df_tracks",
                overwrite=self.colect.overwrite,
            )
        else:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
            sys.exit()

        if not self.colect.overwrite:
            try:
                print_message("Checking...", "Removing duplicated files.", "n")
                old_df = read_json_to_df("df_track_details")
                df_track = self.colect.check_existent_tracks(df_track, old_df)
                print_message("Success", "Duplicates removed", "s")
            except FileNotFoundError:
                print_message("Success", "No file to have duplicates", "s")

        tracks_details = self.colect.search_track_details(df_track)
        print(f"end: {tracks_details['style'].unique()=}")  # debug
        print_message(
            "Success",
            f"{len(tracks_details)} set of detailed tracks collected",
            "s",
        )
        if len(tracks_details) != 0:
            self.colect.write_json(
                tracks_details,
                data_type="df",
                filename="df_track_details",
                overwrite=self.colect.overwrite,
            )
        else:
            print_message(
                "Success",
                "No new data to be saved.",
                "s",
            )
