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

                df_res, exception_raised = self.get_sp_repertoire(
                    search_str, style, year, repertoire_type
                )

                if exception_raised == 2:
                    if len(df_repertoire) != 0:
                        resp = input(
                            f"Got about to {len(df_repertoire)} {repertoire_type}(s)."
                            + " Would you like to proceed? [y/n]: "
                        )
                        if resp.lower() == "y":
                            df_repertoire = pd.concat(
                                [df_repertoire, df_res], ignore_index=True
                            )
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
                    df_repertoire = pd.concat(
                        [df_repertoire, df_res], ignore_index=True
                    )

        return df_repertoire

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
                rest = self.max_repertoire % repertoire_limit
                if rest == 0:
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

        styles_list = []

        for item in result:
            dict_styles = {}

            dict_styles["id"] = item["id"]
            dict_styles["name"] = item["name"].lower()
            dict_styles["artist"] = item["artists"][0]["name"].lower()
            dict_styles["style"] = style
            dict_styles["year"] = year
            dict_styles["release_date"] = item["release_date"]
            dict_styles["n_of_tracks"] = item["n_of_tracks"]

            styles_list.append(dict_styles)

        print_message(
            "Searching...",
            f"Got {len(result)} {repertoire_type} of '{style} {year}'",
            "n",
        )

        df_repertoire = pd.DataFrame(styles_list)

        return df_repertoire

    def search_tracks_from_repertoire(
        self,
        df_repertoire: pd.DataFrame,
        repertoire_type: str = "album",
    ) -> pd.DataFrame:
        """"""
        steps = (len(df_repertoire.index) - 1) // 20
        tracks = []

        for idx_repertoire in range(steps + 1):
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

            album_results, exception_raised = self.get_sp_tracks_in_repertoire(
                repertoire_ids
            )
            if exception_raised == 2:
                break

            trecks_res, exception_raised = self.get_sp_tracks(
                album_results,
                df_repertoire.iloc[idx_repertoire * 20 : (idx_repertoire + 1) * 20],
                repertoire_total_tracks,
                repertoire_type,
            )
            if exception_raised == 2:
                break

            if trecks_res is not None:
                tracks.extend(trecks_res)

        df_track = pd.DataFrame(tracks)

        return df_track

    @exception_handler
    def get_sp_tracks_in_repertoire(self, repertoire_ids: List[str]) -> Dict[str, str]:
        """"""
        album_results = self.sp.albums(repertoire_ids)

        return album_results

    @exception_handler
    def get_styles(self) -> List[str]:
        """Return a list of styles"""
        return self.sp.recommendation_genre_seeds()["genres"]

    @exception_handler
    def get_sp_tracks(
        self,
        album_results: Dict[str, Any],
        df_repertoire_in_loc: pd.DataFrame,
        repertoire_total_tracks: List[int],
        repertoire_type: str,
    ) -> List[dict[str, Any]]:
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
                tracks["repertoire_name"] = df_repertoire_in_loc.iloc[idx_repertoire][
                    "name"
                ]
                tracks["repertoire_id"] = df_repertoire_in_loc.iloc[idx_repertoire][
                    "id"
                ]
                tracks["style"] = df_repertoire_in_loc.iloc[idx_repertoire]["style"]
                tracks["year"] = df_repertoire_in_loc.iloc[idx_repertoire]["year"]

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
    def get_sp_details(self, search_ids: list[str]) -> Dict[str, Any]:
        """"""
        results = self.sp.audio_features(search_ids)
        return results

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
