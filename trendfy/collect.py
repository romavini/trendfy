from argparse import Namespace

from trendfy.params import MAX_REQ_ALBUMS, STYLES, YEARS
from trendfy.trend import Trendfy


def collect(args: Namespace):
    max_repertoire = int(args.collect[0]) if args.collect else MAX_REQ_ALBUMS
    trendfy = Trendfy(max_repertoire, STYLES, YEARS)
    trendfy.colector_runner()


def repair():
    trendfy = Trendfy()
    trendfy.repair()
