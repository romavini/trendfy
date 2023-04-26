import argparse

from trendfy.analyse import analyse
from trendfy.collect import collect, repair
from trendfy.params import MAX_REQ_ALBUMS, STYLES, YEARS
from trendfy.tools import print_message

if __name__ == "__main__":  # pragma: no cover
    print_message("Starting", "Starting module")
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

    if args.collect:  # pragma: no cover
        max_repertoire = int(args.collect[0]) if args.collect else MAX_REQ_ALBUMS
        collect(max_repertoire, STYLES, YEARS)

    if args.analyse:
        analyse()

    if args.repair:
        repair()

    print_message("Finished", "Module fineshed\n\n")
