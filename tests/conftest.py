import pytest
from sqlalchemy import create_engine
from trendfy.helpers import get_dotenv


@pytest.fixture(scope="session")
def generate_engine():
    path_db = (
        f"postgresql://{get_dotenv('user_db')}:"
        f"{get_dotenv('password_db')}@{get_dotenv('host_db')}"
        f":{get_dotenv('port_db')}/{get_dotenv('database_db')}"
    )
    engine = create_engine(path_db)

    yield engine
