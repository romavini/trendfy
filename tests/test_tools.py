from typing import Any, Tuple

import pytest  # type: ignore
from dotenv import load_dotenv
from requests.exceptions import ConnectionError as RequestsConnectionError  # type: ignore
from requests.exceptions import HTTPError, ReadTimeout  # type: ignore
from spotipy.exceptions import SpotifyException  # type: ignore

from trendfy.tools import exception_handler, get_dotenv, get_log_text


@exception_handler
def xfail(error=None):
    if error is None:
        return 2

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
        (RequestsConnectionError, (None, 1)),
        (None, (2, 0)),
    ],
)
def test_exception_handler(error: Exception, expect_tuple: Tuple[int, Any]):
    assert xfail(error) == expect_tuple


def test_exception_handler_keyboard_interrupt():
    with pytest.raises(KeyboardInterrupt):
        xfail(KeyboardInterrupt)


def test_env_file_exist():
    assert load_dotenv()


@pytest.mark.parametrize(
    "env_variable_name",
    [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "user_db",
        "password_db",
        "host_db",
        "port_db",
        "database_db",
    ],
)
def test_get_dotenv(env_variable_name: str):
    assert get_dotenv(env_variable_name) is not None


def test_get_log_text():
    txt = get_log_text()
    assert isinstance(txt, list)
