from trendfy.helpers import get_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import json


class Colect:
    def __init__(self):
        styles = ["sertanejo", "samba", "bossa nova", "funk", "rap", "mpb"]
        years = ["2016", "2017", "2018", "2019", "2020"]

        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=get_dotenv("CLIENT_ID"),
                client_secret=get_dotenv("CLIENT_SECRET"),
            )
        )

        df, result = self.get_playlists(styles, years)
        self.write(df, result)

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
                dict_styles["href"] = result["playlists"]["items"][0][
                    "external_urls"
                ]["spotify"]
                dict_styles["style"] = style

                styles_list.append(dict_styles)

        df = pd.DataFrame(styles_list)

        return df, result

    def write(self, df, result):
        with open("response.json", "w") as f:
            json.dump(result, f)

        with open("responsedf.json", "w") as f:
            result_df = df.to_json(orient="split")
            parsed = json.loads(result_df)
            json.dump(parsed, f)


if __name__ == "__main__":
    colect = Colect()
