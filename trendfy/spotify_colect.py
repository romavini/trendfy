from trendfy.helpers import (
    exception_handler,
    get_dotenv,
    print_message,
)
import sys
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


class Colect:
    def __init__(
        self,
        overwrite: bool = False,
        max_repertoire: int = 100,
        max_ids_request: int = 50,
    ):
        self.overwrite = overwrite
        self.max_repertoire = max_repertoire
        self.max_ids_request = max_ids_request
        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("SPOTIFY_CLIENT_ID"),
                client_secret=get_dotenv("SPOTIFY_CLIENT_SECRET"),
            )
        )

    @exception_handler
    def get_styles(self) -> List[str]:
        """Return a list of styles"""
        return self.sp.recommendation_genre_seeds()["genres"]

    @exception_handler
    def get_sp_repertoire(
        self,
        search_str: str,
        style: str,
        year: int,
        repertoire_type: str,
    ) -> pd.DataFrame:
        """"""
        result = []
        offset = 0
        repertoire_limit = 20

        for i in range((self.max_repertoire // repertoire_limit) + 1):
            if i == (self.max_repertoire // repertoire_limit):
                remaining = self.max_repertoire % repertoire_limit
                if remaining == 0:
                    break

                limit = self.max_repertoire % repertoire_limit
            else:
                limit = repertoire_limit

            result.extend(
                self.sp.search(
                    search_str,
                    type=repertoire_type,
                    limit=limit,
                    offset=offset,
                )[f"{repertoire_type}s"]["items"]
            )
            offset += repertoire_limit

        print_message(
            "Searching...",
            f"Got {len(result)} {repertoire_type} of '{style} {year}'",
            "n",
        )

        return result

    def append_albums_to_df(
        self,
        albums_df: pd.DataFrame,
        albums_response: List[Any],
        style: str,
        year: int,
    ) -> pd.DataFrame:
        """Append the infos of albums in a list of dictionaries."""

        albums_list = []

        for item in albums_response:
            dict_styles = {}

            dict_styles["id"] = item["id"]
            dict_styles["name"] = item["name"].lower()
            dict_styles["artist"] = item["artists"][0]["name"].lower()
            dict_styles["style"] = style
            dict_styles["year"] = year
            dict_styles["release_date"] = item["release_date"]
            dict_styles["n_of_tracks"] = item["total_tracks"]
            dict_styles["artist_id"] = item["artists"][0]["id"]

            albums_list.append(dict_styles)

        df_repertoire = pd.concat(
            [albums_df, pd.DataFrame(albums_list)], ignore_index=True
        )

        return df_repertoire

    def search_repertoires(
        self,
        styles: List[str],
        years: range,
        repertoire_type: str = "album",
    ) -> pd.DataFrame:
        """"""
        df_repertoire = pd.DataFrame()

        for year in years:
            for style in styles:
                search_str = f"{style} year:{year}"

                repertoire_response, exception_raised = self.get_sp_repertoire(
                    search_str, style, year, repertoire_type
                )

                df_repertoire = self.append_albums_to_df(
                    df_repertoire, repertoire_response, style, year
                )

                if exception_raised == 2:
                    if len(df_repertoire) != 0:
                        resp = input(
                            f"Got about to {len(df_repertoire)} {repertoire_type}(s)."
                            + " Would you like to proceed? [y/N]: "
                        ).lower()

                        if resp == "y":

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

        return df_repertoire

    @exception_handler
    def get_sp_tracks_in_repertoire(
        self, repertoire_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """"""
        album_results = self.sp.albums(repertoire_ids)

        return album_results

    def append_track_to_list(
        self,
        tracks: List[Any],
        tracks_response: List[Dict[str, Any]],
        features_response: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Append the infos and features of tracks in a list of dictionaries."""

        for track, feature in zip(tracks_response, features_response):
            tracks_dict = {}

            if track["track_id"] != feature["id"]:
                print_message("Erro", "Some resquest fail.", "e")
                # TODO: merge tracks and features by id in an DataFrame.
            else:
                tracks_dict["id"] = track["track_id"]
                tracks_dict["name"] = track["track_name"]
                tracks_dict["album_id"] = track["album_id"]
                tracks_dict["album_popularity"] = track["album_popularity"]
                tracks_dict["popularity"] = track["popularity"]
                tracks_dict["duration_ms"] = track["duration_ms"]
                tracks_dict["explicit"] = track["explicit"]

                tracks_dict["danceability"] = feature["danceability"]
                tracks_dict["danceability"] = feature["danceability"]
                tracks_dict["danceability"] = feature["danceability"]
                tracks_dict["energy"] = feature["energy"]
                tracks_dict["key"] = feature["key"]
                tracks_dict["loudness"] = feature["loudness"]
                tracks_dict["mode"] = feature["mode"]
                tracks_dict["speechiness"] = feature["speechiness"]
                tracks_dict["acousticness"] = feature["acousticness"]
                tracks_dict["instrumentalness"] = feature["instrumentalness"]
                tracks_dict["liveness"] = feature["liveness"]
                tracks_dict["valence"] = feature["valence"]
                tracks_dict["tempo"] = feature["tempo"]
                tracks_dict["time_signature"] = feature["time_signature"]

                tracks.append(tracks_dict)

        return tracks

    def search_tracks_from_repertoire(
        self,
        df_repertoire: pd.DataFrame,
        repertoire_type: str = "album",
    ) -> pd.DataFrame:
        """"""
        steps = (len(df_repertoire.index) - 1) // 20 + 1
        tracks: List[Any] = []

        for idx_repertoire in range(steps):
            repertoire_ids = df_repertoire.iloc[
                idx_repertoire * 20 : (idx_repertoire + 1) * 20
            ]["id"]
            repertoire_total_tracks = df_repertoire.iloc[
                idx_repertoire * 20 : (idx_repertoire + 1) * 20
            ]["n_of_tracks"].tolist()

            print_message(
                "Searching...",
                f"Getting the {repertoire_type} tracks: "
                f"{round(idx_repertoire * 100 / steps, 2)}%",
                "n",
            )

            # Get the ids of albums
            album_response, exception_raised = self.get_sp_tracks_in_repertoire(
                repertoire_ids
            )
            if exception_raised == 2:
                break

            # Get tracks of the albums
            tracks_response, exception_raised = self.get_sp_tracks(
                album_response,
                df_repertoire.iloc[idx_repertoire * 20 : (idx_repertoire + 1) * 20],
                repertoire_total_tracks,
                repertoire_type,
            )
            if exception_raised == 2:
                break

            # Get details of the tracks
            search_ids = [track["track_id"] for track in tracks_response]
            features_responde, exception_raised = self.get_sp_details(search_ids)

            if exception_raised == 2:
                break

            tracks = self.append_track_to_list(tracks, tracks_response, features_responde)

            if tracks_response is not None:
                tracks.extend(tracks_response)

        df_track = pd.DataFrame(tracks)

        return df_track

    @exception_handler
    def get_sp_tracks(
        self,
        album_results: Dict[str, Any],
        df_repertoire_in_loc: pd.DataFrame,
        repertoire_total_tracks: List[int],
        repertoire_type: str,
    ) -> List[Dict[str, Any]]:
        """"""
        track_list = []

        for idx_repertoire, repertoire in enumerate(album_results["albums"]):
            if repertoire_type == "album":
                tracksids = [item["id"] for item in repertoire["tracks"]["items"]]

            if repertoire_total_tracks[idx_repertoire] != len(
                repertoire["tracks"]["items"]
            ):
                print_message(
                    "Missing tracks!",
                    f"album {df_repertoire_in_loc.iloc[idx_repertoire]['name']} - "
                    f"id:{df_repertoire_in_loc.iloc[idx_repertoire]['id']} should have "
                    f"{repertoire_total_tracks[idx_repertoire]} tracks, "
                    f"but has only {len(repertoire['tracks']['items'])}",
                    "e",
                )

            tracks_popularity = []

            for i in range(((len(tracksids) - 1) // self.max_ids_request) + 1):
                tracks_resp = self.sp.tracks(
                    tracksids[self.max_ids_request * i : self.max_ids_request * (i + 1)]
                )["tracks"]

                tracks_popularity.extend([track["popularity"] for track in tracks_resp])

            for idx_track, item in enumerate(repertoire["tracks"]["items"]):
                tracks = {}

                if item["id"] != tracksids[idx_track]:
                    raise ValueError("Popularity list is out of order")

                tracks["track_id"] = item["id"]
                tracks["track_name"] = item["name"]

                if repertoire_type == "album":
                    tracks["album_id"] = repertoire["id"]
                    tracks["album_popularity"] = repertoire["popularity"]

                tracks["popularity"] = tracks_popularity[idx_track]
                tracks["duration_ms"] = item["duration_ms"]
                tracks["explicit"] = item["explicit"]

                track_list.append(tracks)

        return track_list

    def search_track_details(self, df_track: pd.DataFrame) -> pd.DataFrame:
        """Given tracks id, return details from tracks.

        Keyword arguments:
        df_track -- list of dictionaries with tracks
        """
        ids = list(set(df_track["track_id"]))
        features_list = []

        for i in range(((len(ids) - 1) // self.max_ids_request) + 1):
            search_ids = ids[i * self.max_ids_request : (i + 1) * self.max_ids_request]
            features_responde, exception_raised = self.get_sp_details(search_ids)

            if exception_raised == 2:
                sys.exit()

            if not (features_responde is None):
                features_list.extend(features_responde)

        if len(features_list) == 0:
            print_message(
                "Empty List",
                "No data to proceed. Exiting...",
                "e",
            )
            sys.exit()

        while None in features_list:
            features_list.remove(None)

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
    def get_sp_details(self, search_ids: list[str]) -> List[Dict[str, Any]]:
        """Collect features of any all tracks.

        Keyword arguments:
        search_ids -- List of track ids
        """
        tracks_features = []
        for i in range(((len(search_ids) - 1) // self.max_ids_request) + 1):
            tracks_resp = self.sp.audio_features(
                search_ids[self.max_ids_request * i : self.max_ids_request * (i + 1)]
            )
            tracks_features.extend(tracks_resp)

        return tracks_features

    @staticmethod
    def check_existent_tracks(
        present_df: pd.DataFrame, df_saved: pd.DataFrame
    ) -> pd.DataFrame:
        """"""
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
