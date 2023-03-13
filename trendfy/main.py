from trendfy.params import MAX_REQ_ALBUMS, STYLES, YEARS
from trendfy.trend import Trendfy


def menu() -> int:
    type_error = True
    while type_error:
        resp_max_repertoire = input(
            f"\nMax resquests of repertoire ({MAX_REQ_ALBUMS})\n-->:"
        )
        try:
            if resp_max_repertoire == "":
                max_repertoire = MAX_REQ_ALBUMS
            else:
                max_repertoire = int(resp_max_repertoire)

        except ValueError:
            print("Response must be a number.")
        else:
            type_error = False

    return max_repertoire


if __name__ == "__main__":
    max_repertoire = menu()
    trendfy = Trendfy(max_repertoire, STYLES, YEARS)

    trendfy.colector_runner()
