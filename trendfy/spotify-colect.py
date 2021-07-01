from trendfy.helpers import get_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json


class Colect:
    def __init__(self):
        styles = [
            "sertanejo",
            "samba",
            "bossa nova",
            "funk",
            "rap",
            "pop",
            "mpb",
            "rock",
        ]
        years = [
            "2015",
            "2016",
            "2017",
            "2018",
            "2019",
            "2020",
        ]

        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("CLIENT_ID"),
                client_secret=get_dotenv("CLIENT_SECRET"),
            )
        )

        df, result = self.get_playlists(styles, years)
        self.get_tracks(df)
        # self.write(result)
        # self.write(df, "df")

    def get_playlists(self, styles, years):
        styles_list = []

        for style in styles:
            for year in years:
                dict_styles = {}

                search_str = f"{style} {year}"

                result = self.sp.search(search_str, type="playlist")

                dict_styles["name"] = result["playlists"]["items"][0][
                    "name"
                ].lower()
                dict_styles["id"] = result["playlists"]["items"][0]["id"]
                dict_styles["style"] = style
                dict_styles["year"] = year

                styles_list.append(dict_styles)

        df = pd.DataFrame(styles_list)

        return df, result

    def get_tracks(self, df):
        print("Get Tracks")
        track_list = []

        for idx in df.index:
            print(f"{df.iloc[idx]['style']} {df.iloc[idx]['year']}")

            playlist_id = df.iloc[idx]["id"]
            result = self.sp.playlist(playlist_id)

            for item in result["tracks"]["items"]:
                tracks = {}
                try:
                    if item["track"]["track"]:
                        tracks["track_name"] = item["track"]["name"]
                        tracks["track_id"] = item["track"]["id"]
                        tracks["artist_name"] = item["track"]["artists"][0][
                            "name"
                        ]
                        tracks["artist_id"] = item["track"]["artists"][0]["id"]
                        tracks["duration"] = item["track"]["duration_ms"]
                        tracks["explicit"] = item["track"]["explicit"]
                        tracks["popularity"] = item["track"]["popularity"]
                        tracks["style"] = df.iloc[idx]["style"]
                        tracks["year"] = df.iloc[idx]["year"]

                        track_list.append(tracks)
                except KeyError:
                    print("[KeyError] -> Error in track")
                except TypeError:
                    print("[TypeError] -> Error in track")

        self.write(track_list, filename="tracks")

    @staticmethod
    def write(data, type_data="json", filename="response"):
        if type_data == "json":
            with open(f"{filename}.json", "w") as f:
                json.dump(data, f)

        elif type_data == "df":
            with open(f"{filename}.json", "w") as f:
                result_df = data.to_json(orient="split")
                parsed = json.loads(result_df)
                json.dump(parsed, f)


if __name__ == "__main__":
    colect = Colect()
