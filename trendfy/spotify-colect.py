import numpy as np
from trendfy.helpers import get_dotenv, print_message
import sys
import json
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
from requests.exceptions import HTTPError


class Colect:
    def __init__(self):
        self.overwrite = False
        self.max_playlists = 50
        self.max_ids_request = 50
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("CLIENT_ID"),
                client_secret=get_dotenv("CLIENT_SECRET"),
            )
        )

    def get_playlists(self, styles, years):
        styles_list = []

        for style in styles:
            for year in years:
                try:
                    search_str = f"{style} {year}"

                    result = self.sp.search(
                        search_str, type="playlist", limit=self.max_playlists
                    )

                    for i in range(len(result["playlists"]["items"])):
                        dict_styles = {}

                        dict_styles["name"] = result["playlists"]["items"][i][
                            "name"
                        ].lower()
                        dict_styles["id"] = result["playlists"]["items"][i]["id"]
                        dict_styles["style"] = style
                        dict_styles["year"] = year

                        styles_list.append(dict_styles)

                    print_message(
                        "Searching",
                        f"{len(result['playlists']['items'])} playlists of"
                        + f" '{style}"
                        + f" {year}'",
                        "n",
                    )
                except KeyboardInterrupt:
                    print_message(
                        "KeyboardInterrupt",
                        "Script stopped by user.",
                        "e",
                    )

                    if len(styles_list) != 0:
                        resp = input(
                            f"Got about to {len(styles_list)} items."
                            + " Would you like to proceed? [y/n]: "
                        )
                        if resp.lower() == "y":
                            df_playlist = pd.DataFrame(styles_list)
                            return df_playlist
                        else:
                            sys.exit()
                    else:
                        print_message(
                            "Empty List",
                            "No data to proceed. Exiting...",
                            "e",
                        )
                        sys.exit()

        df_playlist = pd.DataFrame(styles_list)

        return df_playlist

    def get_tracks(self, df_playlist):
        track_list = []

        for idx in df_playlist.index:
            try:
                playlist_id = df_playlist.iloc[idx]["id"]
                result = self.sp.playlist(playlist_id)

                for item in result["tracks"]["items"]:
                    tracks = {}

                    try:
                        if item["track"]["track"]:
                            tracks["track_name"] = item["track"]["name"]
                            tracks["track_id"] = item["track"]["id"]
                            tracks["artist_name"] = item["track"]["artists"][0]["name"]
                            tracks["release_date"] = item["track"]["album"][
                                "release_date"
                            ]
                            tracks["artist_id"] = item["track"]["artists"][0]["id"]
                            tracks["duration"] = item["track"]["duration_ms"]
                            tracks["explicit"] = item["track"]["explicit"]
                            tracks["popularity"] = item["track"]["popularity"]
                            tracks["playlist_name"] = df_playlist.iloc[idx]["name"]
                            tracks["playlist_id"] = df_playlist.iloc[idx]["id"]
                            tracks["style"] = df_playlist.iloc[idx]["style"]
                            tracks["year"] = df_playlist.iloc[idx]["year"]

                            track_list.append(tracks)

                    except KeyError:
                        print_message(
                            "KeyError",
                            "Error in track info. Item dropped.",
                            "e",
                        )
                    except TypeError:
                        print_message(
                            "TypeError",
                            "Error in track info. Item dropped.",
                            "e",
                        )
                    except ConnectionResetError:
                        print_message(
                            "ConnectionResetError",
                            "Connection reset by peer.",
                            "e",
                        )

                        df_track = pd.DataFrame(track_list)
                        return df_track
                    except KeyboardInterrupt:
                        print_message(
                            "KeyboardInterrupt",
                            "Script stopped by user.",
                            "e",
                        )
                        df_track = pd.DataFrame(track_list)
                        return df_track

            except KeyboardInterrupt:
                print_message(
                    "KeyboardInterrupt",
                    "Script stopped by user.",
                    "e",
                )

                if len(track_list) != 0:
                    df_track = pd.DataFrame(track_list)
                    return df_track
                else:
                    print_message(
                        "Empty List",
                        "No data to proceed. Exiting...",
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
        for i in range(len(ids) // self.max_ids_request):
            try:
                print_message(
                    "Getting",
                    f"Details of tracks: set {i} "
                    f"of {len(ids) // self.max_ids_request}",
                    "n",
                )

                results = self.sp.audio_features(
                    ids[i * self.max_ids_request : (i + 1) * self.max_ids_request - 1]
                )

                features_list.extend(results)
            except SpotifyException:
                print_message("SpotifyException", "Error getting request", "e")
                exit_n_save = True
                break
            except HTTPError:
                print_message("HTTPError", "Error getting request", "e")
                exit_n_save = True
                break
            except ConnectionResetError:
                print_message(
                    "ConnectionResetError",
                    "Connection reset by peer.",
                    "e",
                )
                exit_n_save = True
                break
            except KeyboardInterrupt:
                print_message(
                    "KeyboardInterrupt",
                    "Script stopped by user.",
                    "e",
                )
                exit_n_save = True
                break

        if not exit_n_save:
            try:
                print_message(
                    "Getting",
                    f"Details of tracks: set {len(ids) // self.max_ids_request} "
                    f"of {len(ids) // self.max_ids_request}",
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
                    "Connection reset by peer.",
                    "e",
                )

        while None in features_list:
            features_list.remove(None)

        if len(features_list) == 0:
            print_message(
                "Empty List",
                "No data to proceed. Exiting...",
                "e",
            )
            sys.exit()

        try:
            features_df = pd.DataFrame(features_list)
        except AttributeError:
            print_message("AttributeError", "None in list. Saving list...", "e")
            self.write_json(
                features_list, data_type="list", filename="features_list", overwrite=True
            )

        df_track.drop_duplicates(subset=["track_id", "playlist_id"], inplace=True)
        df_details = pd.merge(
            left=df_track,
            right=features_df,
            how="inner",
            left_on="track_id",
            right_on="id",
        ).drop_duplicates(subset=["track_id", "playlist_id"])

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
                    old_df = self.read_json_to_df(filename)
                    data = pd.concat([old_df, data])
                except FileNotFoundError:
                    print_message(
                        "Warning", f"File '{filename}.json' not found. Creating new", "n"
                    )

                with open(f"{filename}.json", "w") as f:
                    result_df = data.to_json(orient="split")
                    parsed = json.loads(result_df)
                    json.dump(parsed, f)

        print_message("Success", f"File '{filename}.json' saved.", "s")

    @staticmethod
    def read_json_to_df(filename="df_track_details"):
        with open(f"{filename}.json", "r") as f:
            dict_json = json.load(f)

        df = pd.DataFrame(dict_json["data"], columns=dict_json["columns"])

        return df

    @staticmethod
    def check_existent_tracks(present_df, df_saved):
        duplicates = np.array(
            [
                (present_track, present_playlist)
                in zip(
                    df_saved["track_id"],
                    df_saved["playlist_id"],
                )
                for present_track, present_playlist in zip(
                    present_df["track_id"],
                    present_df["playlist_id"],
                )
            ]
        )

        if bool(list(duplicates)):
            print_message(
                "Warning",
                f"{len(present_df[duplicates].index)} duplicates identified.",
                "n",
            )
            present_df = present_df.drop(present_df[duplicates].index)
        else:
            print_message(
                "Warning",
                "No duplicates identified.",
                "n",
            )

        present_df.drop_duplicates(subset=["track_id", "playlist_id"], inplace=True)

        return present_df


if __name__ == "__main__":
    styles = [
        "sertanejo",
        "samba",
        "bossa nova",
        "funk",
        "rap",
        "hip hop",
        "pop",
        "mpb",
        "rock",
        "k-pop",
        "folk",
        "metal",
        "country",
        "punk",
        "reggae",
        "soul",
        "jazz",
        "gospel",
    ]
    years = [
        "2011",
        "2012",
        "2013",
        # "2014",
        # "2015",
        # "2016",
        # "2017",
        # "2018",
        # "2019",
        # "2020",
    ]

    colect = Colect()

    df_playlist = colect.get_playlists(styles, years)
    print_message("Success", f"{len(df_playlist)} playlists collected", "s")

    df_track = colect.get_tracks(df_playlist)
    print_message("Success", f"{len(df_track)} tracks collected", "s")

    if not colect.overwrite:
        print_message("Checking", "Removing duplicated files.", "n")
        old_df = colect.read_json_to_df()
        df_track = colect.check_existent_tracks(df_track, old_df)
        print_message("Success", "Duplicates removed", "s")

    if len(df_track) != 0:
        tracks_details = colect.get_track_details(df_track)
        print_message(
            "Success",
            f"{len(tracks_details)} set of detailed tracks collected",
            "s",
        )

        colect.write_json(
            df_track, data_type="df", filename="df_tracks", overwrite=colect.overwrite
        )
        colect.write_json(
            tracks_details,
            data_type="df",
            filename="df_track_details",
            overwrite=colect.overwrite,
        )
        colect.write_json(
            df_playlist,
            data_type="df",
            filename="df_playlist",
            overwrite=colect.overwrite,
        )
    else:
        print_message(
            "Success",
            f"No new data to be saved.",
            "s",
        )
