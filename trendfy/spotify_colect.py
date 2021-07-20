import numpy as np
from trendfy.helpers import exception_handler, get_dotenv, print_message, read_json_to_df
import sys
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Colect:
    def __init__(self):
        self.overwrite = True
        self.max_repertoire = 10
        self.max_ids_request = 50
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("CLIENT_ID"),
                client_secret=get_dotenv("CLIENT_SECRET"),
            )
        )

    def search_repertoires(self, styles, years, repertoire_type="album"):
        """"""
        df_repertoire = pd.DataFrame()

        for year in years:
            for style in styles:
                if repertoire_type == "playlist":
                    search_str = f"{style} {year}"
                elif repertoire_type == "album":
                    search_str = f"{style} year:{year}"

                df_res, exception_raised = self.get_sp_repertoire(
                    search_str, year, style, repertoire_type
                )

                if exception_raised:
                    print(f"{type(df_res)=}")  # debug

                if exception_raised == 2:
                    if (len(df_repertoire) + len(df_res)) != 0:
                        resp = input(
                            f"Got about to {len(df_repertoire)} {repertoire_type}(s)."
                            + " Would you like to proceed? [y/n]: "
                        )
                        if resp.lower() == "y":
                            df_repertoire = pd.concat([df_repertoire, df_res])
                            return df_repertoire
                        else:
                            sys.exit()
                    else:
                        print_message(
                            "Empty List",
                            "No data to proceed. Exiting...",
                            "e",
                        )
                        sys.exit()
                else:
                    df_repertoire = pd.concat([df_repertoire, df_res])

        return df_repertoire

    @exception_handler
    def get_sp_repertoire(self, search_str, year, style, repertoire_type):
        """"""
        result = self.sp.search(
            search_str, type=repertoire_type, limit=self.max_repertoire
        )

        styles_list = []

        for item in result[f"{repertoire_type}s"]["items"]:
            dict_styles = {}

            dict_styles["name"] = item["name"].lower()
            dict_styles["id"] = item["id"]
            dict_styles["total_tracks"] = item["total_tracks"]
            dict_styles["style"] = style
            dict_styles["year"] = year

            if item["type"] == "album":
                dict_styles["release_date"] = item["release_date"]

            styles_list.append(dict_styles)

        print_message(
            "Searching...",
            f"Got {len(result[f'{repertoire_type}s']['items'])}"
            f" {repertoire_type} of '{style} {year}'",
            "n",
        )

        df_repertoire = pd.DataFrame(styles_list)

        return df_repertoire

    def search_tracks_from_repertoire(self, df_repertoire, repertoire_type="album"):
        """"""
        steps = (len(df_repertoire.index) - 1) // 20
        tracks = []

        for idx_repertoire in range(steps + 1):
            repertoire_ids = df_repertoire.iloc[
                idx_repertoire * 20 : (idx_repertoire + 1) * 20
            ]["id"]

            print_message(
                "Searching...",
                f"Getting the {repertoire_type} tracks: "
                f"{round(idx_repertoire * 100 / steps, 2)}%",
                "n",
            )

            album_results, exception_raised = self.get_sp_tracks_in_repertoire(
                repertoire_ids, repertoire_type
            )
            if exception_raised == 2:
                break

            trecks_res, exception_raised = self.get_sp_tracks(
                album_results,
                df_repertoire.iloc[idx_repertoire],
                repertoire_type,
            )
            if exception_raised == 2:
                break

            tracks.extend(trecks_res)

        df_track = pd.DataFrame(tracks)

        return df_track

    @exception_handler
    def get_sp_tracks_in_repertoire(self, repertoire_ids, repertoire_type):
        """"""
        album_results = self.sp.albums(repertoire_ids)

        return album_results

    @exception_handler
    def get_sp_tracks(self, album_results, df_repertoire_in_loc, repertoire_type):
        """"""
        track_list = []

        for repertoire in album_results["albums"]:
            if repertoire_type == "album":
                tracksids = [item["id"] for item in repertoire["tracks"]["items"]]

            tracks_popularity = []

            for i in range(((len(tracksids) - 1) // self.max_ids_request) + 1):
                tracks_popularity.extend(
                    [
                        track["popularity"]
                        for track in self.sp.tracks(
                            tracksids[
                                self.max_ids_request * i : self.max_ids_request * (i + 1)
                            ]
                        )["tracks"]
                    ]
                )

            for idx_track, item in enumerate(repertoire["tracks"]["items"]):
                tracks = {}

                if item["id"] != tracksids[idx_track]:
                    raise ValueError("Popularity list is out of order")

                if repertoire_type == "album":
                    tracks["release_date"] = repertoire["release_date"]
                    tracks["album_popularity"] = repertoire["popularity"]
                    tracks["popularity"] = tracks_popularity[idx_track]

                tracks["track_name"] = item["name"]
                tracks["track_id"] = item["id"]
                tracks["artist_name"] = item["artists"][0]["name"]
                tracks["artist_id"] = item["artists"][0]["id"]
                tracks["duration"] = item["duration_ms"]
                tracks["explicit"] = item["explicit"]
                tracks["repertoire_type"] = repertoire_type
                tracks["repertoire_name"] = df_repertoire_in_loc["name"]
                tracks["repertoire_id"] = df_repertoire_in_loc["id"]
                tracks["style"] = df_repertoire_in_loc["style"]
                tracks["year"] = df_repertoire_in_loc["year"]

                track_list.append(tracks)

        return track_list

    def search_track_details(self, df_track):
        """Given tracks id, return details from tracks.

        Keyword arguments:
        df_track -- list of dictionaries with tracks
        """

        features_list, exception_raised = self.get_sp_details(df_track)
        if exception_raised == 2:
            sys.exit()

        if len(features_list) == 0:
            print_message(
                "Empty List",
                "No data to proceed. Exiting...",
                "e",
            )
            sys.exit()

        features_df = pd.DataFrame(features_list)

        df_track.drop_duplicates(subset=["track_id", "repertoire_id"], inplace=True)
        df_details = pd.merge(
            left=df_track,
            right=features_df,
            how="inner",
            left_on="track_id",
            right_on="id",
        ).drop_duplicates(subset=["track_id", "repertoire_id"])

        return df_details

    @exception_handler
    def get_sp_details(self, df_track):
        """"""
        ids = list(set(df_track["track_id"]))
        features_list = []

        for i in range(((len(ids) - 1) // self.max_ids_request) + 1):
            results = self.sp.audio_features(
                ids[i * self.max_ids_request : (i + 1) * self.max_ids_request]
            )
            features_list.extend(results)

        while None in features_list:
            features_list.remove(None)

        return features_list

    def write_json(self, data, data_type="list", filename="response", overwrite=False):
        if data_type == "list":
            if overwrite:
                with open(f"{filename}.json", "w") as f:
                    json.dump(data, f)
            else:
                pass

        elif data_type == "df":
            if overwrite:
                with open(f"{filename}.json", "w") as f:
                    result_df = data.to_json(orient="split")
                    parsed = json.loads(result_df)
                    json.dump(parsed, f)
            else:
                try:
                    old_df = read_json_to_df(filename)
                    data = pd.concat([old_df, data])
                except FileNotFoundError:
                    print_message(
                        "Warning...",
                        f"File '{filename}.json' not found. Creating new",
                        "n",
                    )

                with open(f"{filename}.json", "w") as f:
                    result_df = data.to_json(orient="split")
                    parsed = json.loads(result_df)
                    json.dump(parsed, f)

        print_message("Success", f"File '{filename}.json' saved.", "s")

    @staticmethod
    def check_existent_tracks(present_df, df_saved):
        duplicates = np.array(
            [
                (present_track, present_playlist)
                in zip(
                    df_saved["track_id"],
                    df_saved["repertoire_id"],
                )
                for present_track, present_playlist in zip(
                    present_df["track_id"],
                    present_df["repertoire_id"],
                )
            ]
        )

        if bool(list(duplicates)):
            print_message(
                "Warning...",
                f"{len(present_df[duplicates].index)} duplicates identified.",
                "n",
            )
            present_df = present_df.drop(present_df[duplicates].index)
        else:
            print_message(
                "Warning...",
                "No duplicates identified.",
                "n",
            )

        present_df.drop_duplicates(subset=["track_id", "repertoire_id"], inplace=True)

        return present_df
