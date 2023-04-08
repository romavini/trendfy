import pandas as pd


class ModelSklearnTrendfy:
    def __init__(self):
        self.df_dict = {}

    def select_training_data(self, df: pd.DataFrame):
        """
        Selects the training data from the dataframe
        :param data: dataframe
        :return: dataframe
        """
        df_features = df.loc[
            :,
            [
                "id_fromtrack",
                "album_id",
                "release_date",
                "name_fromtrack",
                "artist",
                "popularity_fromtrack",
                "duration_ms",
                "explicit",
                "danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo",
                "time_signature",
            ],
        ]
        df_features = df_features.sort_values(by="release_date").set_index("release_date")
        df_100top_table = df_features.sort_values(by="popularity_fromtrack", ascending=False).iloc[:1000].copy()
        df_100lower_table = (
            df_features.query("popularity_fromtrack == 0")
            .sort_values(by="release_date", ascending=False)
            .iloc[:1000]
            .copy()
        )

        self.df_dict["original_df"] = pd.concat(
            [
                df_100top_table.loc[
                    :,
                    [
                        "id_fromtrack",
                        "album_id",
                        "duration_ms",
                        "explicit",
                        "danceability",
                        "energy",
                        "key",
                        "loudness",
                        "mode",
                        "speechiness",
                        "acousticness",
                        "instrumentalness",
                        "liveness",
                        "valence",
                        "tempo",
                        "time_signature",
                    ],
                ],
                df_100lower_table.loc[
                    :,
                    [
                        "id_fromtrack",
                        "album_id",
                        "duration_ms",
                        "explicit",
                        "danceability",
                        "energy",
                        "key",
                        "loudness",
                        "mode",
                        "speechiness",
                        "acousticness",
                        "instrumentalness",
                        "liveness",
                        "valence",
                        "tempo",
                        "time_signature",
                    ],
                ],
            ]
        )

        y_list = [1] * len(df_100top_table)
        y_list += [0] * len(df_100lower_table)

        self.df_dict["original_df"]["class"] = y_list
        self.df_dict["shuffle_df"] = self.df_dict["original_df"].sample(frac=1, random_state=42)

        self.df_dict["y_train"] = self.df_dict["shuffle_df"]["class"]
        self.df_dict["X_train"] = self.df_dict["shuffle_df"].drop(columns=["id_fromtrack", "album_id", "class"]).values
