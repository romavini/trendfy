from typing import List

from trendfy.trend import Trendfy


def collect(max_repertoire: int, styles: List[str], years: range):
    trendfy = Trendfy(max_repertoire, styles, years)
    trendfy.colector_runner()


def repair():
    trendfy = Trendfy()
    trendfy.repair()
