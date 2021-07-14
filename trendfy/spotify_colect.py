import numpy as np
from trendfy.helpers import get_dotenv, print_message, read_json_to_df
import sys
import traceback
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from requests.exceptions import HTTPError, ReadTimeout


class Colect:
    def __init__(self):
        self.overwrite = False
        self.max_repertoire = 50
        self.max_ids_request = 50
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("CLIENT_ID"),
                client_secret=get_dotenv("CLIENT_SECRET"),
            )
        )

    def get_repertoire(self, styles, years, repertoire_type="albums"):
        repertoire_type_single = repertoire_type[:-1]
        styles_list = []

        for style in styles:
            for year in years:
                try:
                    if repertoire_type == "albums":
                        search_str = f"{style} {year}"
                    elif repertoire_type == "albums":
                        search_str = f"{style} year:{year}"

                    result = self.sp.search(
                        search_str, type=repertoire_type_single, limit=self.max_repertoire
                    )

                    for item in result[f"{repertoire_type}"]["items"]:
                        dict_styles = {}

                        dict_styles["name"] = item["name"].lower()
                        dict_styles["id"] = item["id"]
                        dict_styles["style"] = style
                        dict_styles["year"] = year

                        if item["type"] == "album":
                            dict_styles["release_date"] = item["release_date"]

                        styles_list.append(dict_styles)

                    print_message(
                        "Searching...",
                        f"Got {len(result[f'{repertoire_type}']['items'])}"
                        f" {repertoire_type} of '{style} {year}'",
                        "n",
                    )
                except KeyboardInterrupt:
                    print_message(
                        "KeyboardInterrupt",
                        "Step stopped by user.",
                        "e",
                    )

                    if len(styles_list) != 0:
                        resp = input(
                            f"Got about to {len(styles_list)} {repertoire_type}."
                            + " Would you like to proceed? [y/n]: "
                        )
                        if resp.lower() == "y":
                            df_repertoire = pd.DataFrame(styles_list)
                            return df_repertoire
                        else:
                            sys.exit()
                    else:
                        print_message(
                            "Empty List",
                            f"No data to proceed. Exiting.\n{traceback.format_exc()}..",
                            "e",
                        )
                        sys.exit()

        df_repertoire = pd.DataFrame(styles_list)

        return df_repertoire

    def get_tracks_from_repertoire(self, df_repertoire, repertoire_type="albums"):
        track_list = []

        print_message(
            "Searching...",
            f"Getting the {repertoire_type[:-1]} tracks",
            "n",
        )

        steps = len(df_repertoire.index) // 20 + 1

        for idx_repertoire in range(steps):
            if len(steps) < 1e3:
                print_message(
                    "Searching...",
                    f"Getting the {repertoire_type[:-1]} tracks: "
                    f"{round(idx_repertoire * 100 / steps, 2)}%",
                    "n",
                )
            elif len(steps) < 1e4 and (idx_repertoire % 10 == 0):
                print_message(
                    "Searching...",
                    f"Getting the {repertoire_type[:-1]} tracks: "
                    f"{round(idx_repertoire * 100 / steps, 2)}%",
                    "n",
                )

            try:
                repertoire_ids = df_repertoire.iloc[
                    idx_repertoire * 20 : (idx_repertoire + 1) * 20
                ]["id"]
                results = self.sp.albums(repertoire_ids)

                for repertoire in results["albums"]:
                    tracks_popularity = []

                    if repertoire_type == "albums":
                        for _ in range(len(repertoire["tracks"]["items"]) // 50 + 1):
                            tracksids = [
                                item["id"] for item in repertoire["tracks"]["items"]
                            ]
                            tracks_popularity.append(
                                [
                                    track["popularity"]
                                    for track in self.sp.tracks(tracksids)["tracks"]
                                ]
                            )

                    for idx_track, item in enumerate(repertoire["tracks"]["items"]):
                        tracks = {}

                        try:
                            if repertoire_type == "albums":
                                tracks["release_date"] = repertoire["release_date"]
                                tracks["popularity"] = tracks_popularity[0][idx_track]

                            tracks["track_name"] = item["name"]
                            tracks["track_id"] = item["id"]
                            tracks["artist_name"] = item["artists"][0]["name"]
                            tracks["artist_id"] = item["artists"][0]["id"]
                            tracks["duration"] = item["duration_ms"]
                            tracks["explicit"] = item["explicit"]

                            tracks["repertoire_type"] = repertoire_type
                            tracks["repertoire_name"] = df_repertoire.iloc[
                                idx_repertoire
                            ]["name"]
                            tracks["repertoire_id"] = df_repertoire.iloc[idx_repertoire][
                                "id"
                            ]
                            tracks["style"] = df_repertoire.iloc[idx_repertoire]["style"]
                            tracks["year"] = df_repertoire.iloc[idx_repertoire]["year"]

                            track_list.append(tracks)

                        except KeyError:
                            print_message(
                                "KeyError",
                                "Error in track info. Item dropped."
                                f"\n{traceback.format_exc()}",
                                "e",
                            )
                        except TypeError:
                            print_message(
                                "TypeError",
                                "Error in track info. Item dropped."
                                f"\n{traceback.format_exc()}",
                                "e",
                            )
                        except ConnectionResetError:
                            print_message(
                                "ConnectionResetError",
                                f"Connection reset by peer.\n{traceback.format_exc()}",
                                "e",
                            )

                            df_track = pd.DataFrame(track_list)
                            return df_track
                        except KeyboardInterrupt:
                            print_message(
                                "KeyboardInterrupt",
                                "Step stopped by user.",
                                "e",
                            )
                            df_track = pd.DataFrame(track_list)
                            return df_track

            except ReadTimeout:
                print_message(
                    "ReadTimeout",
                    f"Read timed out.\n{traceback.format_exc()}",
                    "e",
                )

                if len(track_list) != 0:
                    df_track = pd.DataFrame(track_list)
                    return df_track
                else:
                    print_message(
                        "Empty List",
                        f"No data to proceed. Exiting...\n{traceback.format_exc()}",
                        "e",
                    )
                    sys.exit()

            except ConnectionResetError:
                print_message(
                    "ConnectionError",
                    f"Connection reset by peer.\n{traceback.format_exc()}",
                    "e",
                )

                if len(track_list) != 0:
                    df_track = pd.DataFrame(track_list)
                    return df_track
                else:
                    print_message(
                        "Empty List",
                        f"No data to proceed. Exiting...\n{traceback.format_exc()}",
                        "e",
                    )
                    sys.exit()

            except KeyboardInterrupt:
                print_message(
                    "KeyboardInterrupt",
                    "Step stopped by user.",
                    "e",
                )

                if len(track_list) != 0:
                    df_track = pd.DataFrame(track_list)
                    return df_track
                else:
                    print_message(
                        "Empty List",
                        f"No data to proceed. Exiting...\n{traceback.format_exc()}",
                        "e",
                    )
                    sys.exit()

            df_track = pd.DataFrame(track_list)

        return df_track

    def get_track_details(self, df_track):
        """Given tracks id, return details from tracks.

        Keyword arguments:
        df_track -- list of dictionaries with tracks
        """
        exit_n_save = False
        ids = list(set(df_track["track_id"]))

        features_list = []
        steps = range(len(ids) // self.max_ids_request)

        for i in steps:
            try:
                if len(steps) < 1e3:
                    print_message(
                        "Searching...",
                        "Getting details of tracks: "
                        f"{round(i * 100 / (len(ids) // self.max_ids_request + 1), 2)}%",
                        "n",
                    )
                elif len(steps) < 1e4 and (i % 10 == 0):
                    print_message(
                        "Searching...",
                        "Getting details of tracks: "
                        f"{round(i * 100 / (len(ids) // self.max_ids_request + 1), 2)}%",
                        "n",
                    )
                elif i % 100 == 0:
                    print_message(
                        "Searching...",
                        "Getting details of tracks: "
                        f"{round(i * 100 / (len(ids) // self.max_ids_request + 1), 2)}%",
                        "n",
                    )

                results = self.sp.audio_features(
                    ids[i * self.max_ids_request : (i + 1) * self.max_ids_request - 1]
                )

                features_list.extend(results)
            except ReadTimeout:
                print_message("ReadTimeout", "Read timed out.", "e")
                exit_n_save = True
                break
            except SpotifyException:
                print_message("SpotifyException", "Error getting request.", "e")
                exit_n_save = True
                break
            except HTTPError:
                print_message("HTTPError", "Error getting request.", "e")
                exit_n_save = True
                break
            except ConnectionResetError:
                print_message(
                    "ConnectionResetError",
                    f"Connection reset by peer.\n{traceback.format_exc()}",
                    "e",
                )
                exit_n_save = True
                break
            except KeyboardInterrupt:
                print_message(
                    "KeyboardInterrupt",
                    "Step stopped by user.",
                    "e",
                )
                exit_n_save = True
                break

        if not exit_n_save:
            try:
                print_message(
                    "Searching...",
                    "Getting details of tracks: 100%",
                    "n",
                )

                results = self.sp.audio_features(
                    ids[len(ids) // self.max_ids_request * self.max_ids_request : -1]
                )

                features_list.extend(results)
            except SpotifyException:
                print_message("SpotifyException", "Error getting request", "e")
            except HTTPError:
                print_message("HTTPError", "Error getting request", "e")
            except ConnectionResetError:
                print_message(
                    "ConnectionResetError",
                    f"Connection reset by peer.\n{traceback.format_exc()}",
                    "e",
                )

        while None in features_list:
            features_list.remove(None)

        if len(features_list) == 0:
            print_message(
                "Empty List",
                f"No data to proceed. Exiting.\n{traceback.format_exc()}..",
                "e",
            )
            sys.exit()

        try:
            features_df = pd.DataFrame(features_list)
        except AttributeError:
            print_message("AttributeError", "None in list. Saving list...", "e")
            self.write_json(
                features_list,
                data_type="list",
                filename="features_list",
                overwrite=True,
            )

        df_track.drop_duplicates(subset=["track_id", "repertoire_id"], inplace=True)
        df_details = pd.merge(
            left=df_track,
            right=features_df,
            how="inner",
            left_on="track_id",
            right_on="id",
        ).drop_duplicates(subset=["track_id", "repertoire_id"])

        return df_details

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
