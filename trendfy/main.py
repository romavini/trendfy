from typing import Tuple
from trendfy.params import STYLES, YEARS
from trendfy.trend import Trendfy


def menu() -> Tuple[bool, int, int, str]:
    resp_overwrite = input(
        "\n\nWould you like to overwrite existing data? [y/N]\n-->:"
    ).lower()
    overwrite = True if resp_overwrite == "y" else False

    type_error = True
    while type_error:
        resp_max_repertoire = input("Max resquests of repertoire\n-->:")
        try:
            if resp_max_repertoire == "":
                max_repertoire = 50
            else:
                max_repertoire = int(resp_max_repertoire)

        except ValueError:
            print("Response must be a number.")
        else:
            type_error = False

    type_error = True
    while type_error:
        resp_max_tracks = input("\n\nMax resquests of tracks\n-->:")
        try:
            if resp_max_tracks == "":
                max_ids_request = 30
            else:
                max_ids_request = int(resp_max_tracks)
        except ValueError:
            print("Response must be a number.")
        else:
            type_error = False

    resp_start_from = input(
        "\n\nWhere would you like to begin? [B: begin / t: tracks / d: details]\n-->:"
    ).lower()
    start_from = resp_start_from if resp_start_from in ["b", "t", "d"] else "b"

    return overwrite, max_repertoire, max_ids_request, start_from


if __name__ == "__main__":
    [overwrite, max_repertoire, max_ids_request, start_from] = menu()
    trendfy = Trendfy(overwrite, max_repertoire, max_ids_request, start_from)

    trendfy.colector_runner(STYLES, YEARS, repertoire_type="album")
