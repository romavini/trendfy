import logging
import os
import traceback
from typing import Any, Callable, Tuple

from dotenv import load_dotenv
from requests.exceptions import ConnectionError, HTTPError, ReadTimeout  # type: ignore
from spotipy.exceptions import SpotifyException


def exception_handler(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def wrapper(*args, **kwargs) -> Tuple[Any, int]:
        res = None
        exception_raised = 1

        try:
            res = func(*args, **kwargs)
        except AttributeError:
            print_message(
                "AttributeError",
                f"\n{traceback.format_exc()}",
                "e",
            )
        except ValueError:
            print_message(
                "ValueError",
                f"\n{traceback.format_exc()}",
                "e",
            )
        except KeyError:
            print_message(
                "KeyError",
                f"Error in track info.\n{traceback.format_exc()}",
                "e",
            )
        except TypeError:
            print_message(
                "TypeError",
                f"Error in track info.\n{traceback.format_exc()}",
                "e",
            )
        except ReadTimeout:
            print_message(
                "ReadTimeout",
                f"Read timed out.\n{traceback.format_exc()}",
                "e",
            )
        except HTTPError:
            print_message(
                "HTTPError",
                f"Error getting request.\n{traceback.format_exc()}",
                "e",
            )
        except SpotifyException:
            print_message(
                "SpotifyException",
                f"Error getting request.\n{traceback.format_exc()}",
                "e",
            )
        except ConnectionResetError:
            print_message(
                "ConnectionResetError",
                f"Connection reset by peer.\n{traceback.format_exc()}",
                "e",
            )
        except ConnectionError:
            print_message(
                "ConnectionError",
                f"Connection aborted.\n{traceback.format_exc()}",
                "e",
            )
        except KeyboardInterrupt:
            print_message(
                "KeyboardInterrupt",
                "Step stopped by user.",
                "e",
            )
            exception_raised = 2
        else:
            exception_raised = 0

        return res, exception_raised

    return wrapper


def print_message(status: str, text: Any, message_type: str = "n"):
    """Print error given Exception

    Keyword argument:
    status -- message type
    message_type -- type of message print. can be 'e' for error, 's' for
    success, and 'n' for notification.
    """
    logging_format = f"%(asctime)s - {__name__} - %(levelname)s:\n%(message)s"
    logging.basicConfig(format=logging_format, level=logging.INFO, datefmt="%d-%m-%Y %H:%M:%S")

    if message_type == "e":
        message_color = "\033[91m"
        eom = ""
    elif message_type == "s":
        message_color = "\033[32m"
        eom = "\n"
    elif message_type == "n":
        message_color = "\033[33m"
        eom = ""

    logging.info(
        "[" + message_color + f"{status}" + "\033[0m" + "]" + message_color + " -> " + "\033[0m" + f"{text}{eom}"
    )


def get_dotenv(envname):
    load_dotenv()
    return os.getenv(f"{envname}")
