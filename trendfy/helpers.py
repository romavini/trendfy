import os

from dotenv import load_dotenv


def print_message(status: str, text: str, message_type: str = "n"):
    """Print error given Exception

    Keyword argument:
    status -- message type
    message_type -- type of message print. can be 'e' for error, 's' for
    success, and 'n' for notification.
    """
    if message_type == "e":
        message_color = "\033[91m"
    elif message_type == "s":
        message_color = "\033[32m"
    elif message_type == "n":
        message_color = "\033[33m"

    print(
        "["
        + message_color
        + f"{status}"
        + "\033[0m"
        + "]"
        + message_color
        + " -> "
        + "\033[0m"
        + f"{text}"
    )


def get_dotenv(envname):
    load_dotenv()
    return os.getenv(f"SPOTIFY_{envname}")
