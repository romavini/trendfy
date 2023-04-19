import argparse

from trendfy.analyse import analyse
from trendfy.collect import collect, repair

if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser(
        description="Spotify Data Process.",
    )
    parser.add_argument(
        "-c",
        "--collect",
        metavar="collect",
        type=int,
        nargs=1,
        help="An integer for maximus of the albuns by year",
    )
    parser.add_argument(
        "-a",
        "--analyse",
        action="store_true",
        help="Return an analisys of the saved data in database",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")

    parser.add_argument(
        "-r",
        "--repair",
        action="store_true",
        help="Check if all tracks of albuns are saved and save those ones that are not",
    )

    args = parser.parse_args()

    if args.collect:
        collect(args)

    if args.analyse:
        analyse()

    if args.repair:
        repair()
