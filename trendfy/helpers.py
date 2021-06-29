import os

from dotenv import load_dotenv


def get_dotenv(envname):
    load_dotenv()
    return os.getenv(f"SPOTIFY_{envname}")
