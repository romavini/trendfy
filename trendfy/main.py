from trendfy.params import STYLES, YEARS
from trendfy.trend import Trendfy


if __name__ == "__main__":
    trendfy = Trendfy()
    # trendfy.colect_tracks(STYLES, YEARS, type="playlist")
    trendfy.colect_tracks(STYLES, YEARS, repertoire_type="albums")
