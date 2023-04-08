from typing import Any, Tuple

import pytest
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout  # type: ignore
from spotipy.exceptions import SpotifyException

from trendfy.helpers import exception_handler


@exception_handler
def xfail(error=None):
    if error is None:
        return 2
    else:
        raise error


@pytest.mark.parametrize(
    "error,expect_tuple",
    [
        (AttributeError, (None, 1)),
        (ValueError, (None, 1)),
        (KeyError, (None, 1)),
        (TypeError, (None, 1)),
        (ReadTimeout, (None, 1)),
        (HTTPError, (None, 1)),
        (SpotifyException, (None, 1)),
        (ConnectionResetError, (None, 1)),
        (ConnectionError, (None, 1)),
        (KeyboardInterrupt, (None, 2)),
        (None, (2, 0)),
    ],
)
def test_exception_handler(error: Exception, expect_tuple: Tuple[int, Any]):
    assert xfail(error) == expect_tuple
