import pytest

from trendfy.collect import collect, repair
from trendfy.errors import EmptyData
from trendfy.tools import get_log_text


def test_collect():
    with pytest.raises(EmptyData):
        collect(0, ["rock"], range(2000, 2001))


def test_repair():
    pass
    # repair()
    # logs = get_log_text()

    # assert "Success" in logs[-1]
    # assert "tracks to be added in DB" in logs[-1]
