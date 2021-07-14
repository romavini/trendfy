from trendfy.spotify_colect import Colect
from trendfy.helpers import print_message, read_json_to_df


class Trendfy:
    def __init__(self):
        self.colect = Colect()

    def colect_tracks(self, styles, years, repertoire_type="albums"):
        df_repertoire = self.colect.get_repertoire(styles, years, repertoire_type)
        print_message("Success", f"{len(df_repertoire)} {repertoire_type} collected", "s")

        df_track = self.colect.get_tracks_from_repertoire(df_repertoire, repertoire_type)
        print_message("Success", f"{len(df_track)} tracks collected", "s")

        if not self.colect.overwrite:
            try:
                print_message("Checking...", "Removing duplicated files.", "n")
                old_df = read_json_to_df("df_track_details")
                df_track = self.colect.check_existent_tracks(df_track, old_df)
                print_message("Success", "Duplicates removed", "s")
            except FileNotFoundError:
                print_message("Success", "No file to have duplicates", "s")

        if len(df_track) != 0:
            tracks_details = self.colect.get_track_details(df_track)
            print_message(
                "Success",
                f"{len(tracks_details)} set of detailed tracks collected",
                "s",
            )

            self.colect.write_json(
                df_track,
                data_type="df",
                filename="df_tracks",
                overwrite=self.colect.overwrite,
            )
            self.colect.write_json(
                tracks_details,
                data_type="df",
                filename="df_track_details",
                overwrite=self.colect.overwrite,
            )
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
