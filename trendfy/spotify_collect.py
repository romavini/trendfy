import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import numpy as np
import pandas as pd
import spotipy  # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials  # type: ignore

from trendfy.errors import EmptyData  # type: ignore
from trendfy.tools import exception_handler, get_dotenv, print_message


class Colect:
    def __init__(
        self,
        max_repertoire: Optional[int] = 100,
        styles: Optional[List[str]] = None,
        years: Optional[range] = None,
    ):
        if styles is not None:
            self.styles = styles
        if years is not None:
            self.years = years
        self.limit_by_request = 30
        self.max_repertoire = max_repertoire
        self.spot = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("SPOTIFY_CLIENT_ID"),
                client_secret=get_dotenv("SPOTIFY_CLIENT_SECRET"),
            )
        )

    @exception_handler
    def get_styles(self) -> List[str]:
        """Return a list of styles"""
        styles = self.spot.recommendation_genre_seeds()["genres"]

        return styles

    @exception_handler
    def get_spot_repertoire(
        self,
        search_str: str,
        style: str,
        year: int,
    ) -> pd.DataFrame:
        """Return list of albuns or playlist given a search"""
        if self.max_repertoire is None:
            self.max_repertoire = 10

        result = []
        offset = 0
        repertoire_limit = 20

        for batch in range((self.max_repertoire // repertoire_limit) + 1):
            if batch == (self.max_repertoire // repertoire_limit):
                remaining = self.max_repertoire % repertoire_limit
                if remaining == 0:
                    break

                limit = self.max_repertoire % repertoire_limit
            else:
                limit = repertoire_limit

            result.extend(
                self.spot.search(
                    search_str,
                    type="album",
                    limit=limit,
                    offset=offset,
                )[
                    "albums"
                ]["items"]
            )
            offset += repertoire_limit

        print_message(
            "Searching...",
            f"Got {len(result)} albums of '{style} {year}'",
            "n",
        )

        return result

    def append_albums_to_df(
        self,
        albums_response: List[Any],
        style: str,
        year: int,
    ) -> pd.DataFrame:
        """Append the infos of albums in a list of dictionaries."""

        albums_list = []
        if not albums_response:
            raise EmptyData

        for item in albums_response:
            dict_styles = {}
            dict_styles["id"] = item["id"]
            dict_styles["name"] = item["name"].lower()
            dict_styles["artist"] = item["artists"][0]["name"].lower()
            dict_styles["style"] = style
            dict_styles["year"] = year
            dict_styles["release_date"] = item["release_date"]
            print(dict_styles["release_date"])
            dict_styles["n_of_tracks"] = item["total_tracks"]
            dict_styles["artist_id"] = item["artists"][0]["id"]

            albums_list.append(dict_styles)

        return pd.DataFrame(albums_list)

    def iter_search_repertoires(
        self,
    ) -> pd.DataFrame:
        """Return the response of the search given years and styles"""

        df_repertoire = pd.DataFrame()
        for year in self.years:
            for style in self.styles:
                df_repertoire = pd.concat([df_repertoire, self.search_repertoires(style, year)], ignore_index=True)

        return df_repertoire

    def search_repertoires(self, style: str, year: int) -> pd.DataFrame:
        search_str = f"{style} year:{year}"
        try:
            repertoire_response, _ = self.get_spot_repertoire(search_str, style, year)
            new_df = self.append_albums_to_df(repertoire_response, style, year)

            return new_df
        except KeyboardInterrupt:
            if len(new_df) == 0:
                print_message(
                    "Empty List",
                    "No data to proceed. Exiting...",
                    "e",
                )
                sys.exit()

            resp = input(f"Got about to {len(new_df)} " f"album(s)." " Would you like to proceed? [y/N]: ").lower()

            if resp == "y":
                return new_df

            sys.exit()

    @exception_handler
    def get_spot_tracks_in_repertoire(self, repertoire_ids: List[str]) -> List[Dict[str, Any]]:
        """Collect track ids of a repertoire"""
        album_results = self.spot.albums(repertoire_ids)

        if album_results is None:
            raise EmptyData

        return album_results

    def append_track_to_list(
        self,
        tracks: List[Any],
        tracks_response: Iterable[Dict[str, Any]],
        features_response: Iterable[Dict[str, Any]],
        release_dates: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        """Append the features of tracks in a list of dictionaries."""

        for track, feature in zip(tracks_response, features_response):
            tracks_dict = {}

            if track is None or feature is None:
                continue

            if track["track_id"] != feature["id"]:
                print_message("Erro", "Some resquest fail.", "e")
                # TODO: merge tracks and features by id in an DataFrame.
            else:
                tracks_dict["id"] = track["track_id"]
                tracks_dict["name"] = track["track_name"]
                tracks_dict["album_id"] = track["album_id"]
                tracks_dict["album_popularity"] = track["album_popularity"]
                tracks_dict["release_date"] = datetime.strptime(release_dates[track["album_id"]], "%Y-%m-%d")
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
    ) -> pd.DataFrame:
        """Collect track data given an repertoires"""
        steps = (len(df_repertoire.index) - 1) // 20 + 1
        tracks: List[Any] = []

        for batch_repertoire in range(steps):
            try:
                repertoire_ids = df_repertoire.iloc[batch_repertoire * 20 : (batch_repertoire + 1) * 20]["id"].copy()
                repertoire_total_tracks = df_repertoire.iloc[batch_repertoire * 20 : (batch_repertoire + 1) * 20][
                    "n_of_tracks"
                ].tolist()

                print_message(
                    "Searching...",
                    f"Getting the album's tracks: " f"{round(batch_repertoire * 100 / steps, 2)}%",
                    "n",
                )

                # Get the ids of albums
                album_response, _ = self.get_spot_tracks_in_repertoire(repertoire_ids)

                # Get tracks of the albums
                tracks_response, _ = self.get_spot_tracks(
                    album_response,
                    df_repertoire.iloc[batch_repertoire * 20 : (batch_repertoire + 1) * 20],
                    repertoire_total_tracks,
                )

                # Get details of the tracks
                search_ids = [track["track_id"] for track in tracks_response]
                release_dates = (
                    pd.DataFrame(album_response["albums"])
                    .loc[:, ["id", "release_date"]]
                    .set_index("id", drop=True)
                    .to_dict()["release_date"]
                )
                print(release_dates)
                features_responde, _ = self.get_spot_details(search_ids)

                tracks = self.append_track_to_list(tracks, tracks_response, features_responde, release_dates)

            except KeyboardInterrupt:
                break

            except EmptyData:
                continue

        df_track = pd.DataFrame(tracks)

        return df_track

    @exception_handler
    def get_spot_tracks(
        self,
        album_results: Dict[str, Any],
        df_repertoire_in_loc: pd.DataFrame,
        repertoire_total_tracks: List[int],
    ) -> List[Dict[str, Any]]:
        """Collect tracks"""
        track_list = []
        for idx_repertoire, repertoire in enumerate(album_results["albums"]):
            tracks_ids = [item["id"] for item in repertoire["tracks"]["items"]]

            if repertoire_total_tracks[idx_repertoire] != len(repertoire["tracks"]["items"]):
                print_message(
                    "Missing tracks!",
                    "\n Album "
                    f"'{df_repertoire_in_loc.iloc[idx_repertoire]['name']}'"
                    " - id: "
                    f"{df_repertoire_in_loc.iloc[idx_repertoire]['id']}"
                    " should have "
                    f"{repertoire_total_tracks[idx_repertoire]} tracks, "
                    f"but has only {len(repertoire['tracks']['items'])}",
                    "e",
                )

            tracks_popularity = self.get_tracks_popularity(tracks_ids)

            track_list.extend(self.get_track_list(repertoire, tracks_ids, tracks_popularity))

        if track_list is None:
            raise EmptyData

        return track_list

    def get_tracks_popularity(self, tracksids: List[str]) -> List[int]:
        tracks_popularity = []

        for batch in range(((len(tracksids) - 1) // self.limit_by_request) + 1):
            tracks_resp = self.spot.tracks(
                tracksids[self.limit_by_request * batch : self.limit_by_request * (batch + 1)]
            )["tracks"]

            tracks_popularity.extend([track["popularity"] for track in tracks_resp])
        return tracks_popularity

    def get_track_list(
        self, repertoire: Dict[str, Any], tracks_ids: List[str], tracks_popularity: List[int]
    ) -> List[Dict[str, Any]]:
        temp_tracks = []
        for idx_track, item in enumerate(repertoire["tracks"]["items"]):
            tracks = {}
            if item["id"] != tracks_ids[idx_track]:
                raise ValueError("Popularity list is out of order")

            tracks["track_id"] = item["id"]
            tracks["track_name"] = item["name"]

            tracks["album_id"] = repertoire["id"]
            tracks["album_popularity"] = repertoire["popularity"]

            tracks["popularity"] = tracks_popularity[idx_track]
            tracks["duration_ms"] = item["duration_ms"]
            tracks["explicit"] = item["explicit"]
            temp_tracks.append(tracks)

        return temp_tracks

    def search_track_details(self, df_track: pd.DataFrame) -> pd.DataFrame:
        """Given tracks id, return details from tracks.

        Keyword arguments:
        df_track -- list of dictionaries with tracks
        """
        ids = list(set(df_track["track_id"]))
        features_list: List[Any] = []

        for batch in range(((len(ids) - 1) // self.limit_by_request) + 1):
            search_ids = ids[self.limit_by_request * batch : self.limit_by_request * (batch + 1)]
            features_response, _ = self.get_spot_details(search_ids)

            features_list = self.insert_into_features(features_list, features_response)

        if len(features_list) == 0:
            print_message(
                "Empty List",
                "No data to proceed. Exiting...",
                "e",
            )
            sys.exit()

        features_list = [feature for feature in features_list if feature is not None]
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

    def insert_into_features(self, features_list: List[Any], features_response: List[Any]) -> List[Any]:
        if features_response is not None:
            features_list.extend(features_response)

        return features_list

    @exception_handler
    def get_spot_details(self, search_ids: List[str]) -> List[Dict[str, Any]]:
        """Collect features of any all tracks.

        Keyword arguments:
        search_ids -- List of track ids
        """
        tracks_features = []
        for batch in range(((len(search_ids) - 1) // self.limit_by_request) + 1):
            tracks_resp = self.spot.audio_features(
                search_ids[self.limit_by_request * batch : self.limit_by_request * (batch + 1)]
            )
            tracks_features.extend(tracks_resp)

        if tracks_features is None:
            raise EmptyData

        return tracks_features

    @staticmethod
    def check_existent_tracks(present_df: pd.DataFrame, df_saved: pd.DataFrame) -> pd.DataFrame:
        """Collect track ids from DB and compare to not save duplicates"""
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
