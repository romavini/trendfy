import argparse

from trendfy.analyse import analyse
from trendfy.collect import collect

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Spotify Data Process.",
    )
    parser.add_argument(
        "-c",
        "--collect",
        metavar="collect",
        type=int,
        nargs=1,
        help="an integer for maximus of the albuns by year",
    )
    parser.add_argument(
        "-a",
        "--analyse",
        action="store_true",
        help="an integer for maximus of the albuns by year",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()

    if args.collect:
        collect(args)

    if args.analyse:
        analyse()
