import inspect
import logging
import os
import traceback
from pathlib import Path
from typing import Any, List, Tuple

from dotenv import load_dotenv  # type: ignore
from requests.exceptions import ConnectionError as RequestConnectionError  # type: ignore
from requests.exceptions import HTTPError, ReadTimeout  # type: ignore
from spotipy.exceptions import SpotifyException  # type: ignore


def exception_handler(function: Any) -> Any:
    def wrapper(*args, **kwargs) -> Tuple[Any, int]:
        response = None
        exception_raised = 1

        try:
            response = function(*args, **kwargs)
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
        except RequestConnectionError:
            print_message(
                "RequestConnectionError",
                f"Connection aborted.\n{traceback.format_exc()}",
                "e",
            )
        # except KeyboardInterrupt as exc:
        #     raise KeyboardInterrupt from exc
        else:
            exception_raised = 0

        return response, exception_raised

    return wrapper


def print_colored_message(status: str, text: Any, message_type: str = "n"):  # pragma: no cover
    """Print error given Exception

    Keyword argument:
    status -- message type
    message_type -- type of message print. can be 'e' for error, 's' for
    success, and 'n' for notification.
    """
    log_folder = get_log_folder()
    logging_format = f"%(asctime)s - {__name__} - %(levelname)s:\n%(message)s"
    logging.basicConfig(
        filename=log_folder / "logs.log",
        format=logging_format,
        level=logging.INFO,
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    if message_type == "e":
        message_color = "\033[91m"
        eom = ""
    elif message_type == "s":
        message_color = "\033[32m"
        eom = "\n"
    elif message_type == "n":
        message_color = "\033[33m"
        eom = ""

    message = "[" + message_color + f"{status}" + "\033[0m" + "]" + message_color + " -> " + "\033[0m" + f"{text}{eom}"
    logging.info(message)


def print_message(status: str, text: Any, message_type: str = "n"):  # pragma: no cover
    """Print error given Exception

    Keyword argument:
    status -- message type
    message_type -- type of message print. can be 'e' for error, 's' for
    success, and 'n' for notification.
    """
    message_type = "Info" if message_type == "n" else "Success" if message_type == "s" else "Error"
    caller_filename = inspect.stack()[1].filename

    log_folder = get_log_folder()
    logging_format = f"%(asctime)s - {caller_filename} - %(levelname)s:\n%(message)s"
    log_filepath = log_folder / "logs.log"
    logging.basicConfig(
        filename=log_filepath,
        format=logging_format,
        level=logging.INFO,
        datefmt="%d-%m-%Y %H:%M:%S",
    )
    message = f"[{status}] -> {text}"
    logging.info(message)


def get_log_folder():
    root = Path(__file__).parent.parent.resolve()
    os.makedirs(root / "logs", exist_ok=True)
    return root / "logs"


def get_dotenv(envname: str) -> Any:
    load_dotenv()
    return os.getenv(f"{envname}")


def get_log_text() -> List[str]:
    root = Path(__file__).parent.parent.resolve()
    with open(root / "logs/logs.log", "r", encoding="UTF-8") as file:
        file_text = file.read()

    logs = file_text.split("\n\n") if "\n\n" in file_text else [file_text]
    logs = [log.strip() for log in logs if log]
    return logs
