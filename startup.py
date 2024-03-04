from sqlalchemy.exc import OperationalError
from database import create_database_tables, get_highest_id
from bgg_api import get_new_data


def check_db_connection(engine) -> None:
    """
    Checks if the app can connect to the database successfully.

    Args:
        engine: The SQLAlchemy engine object used for database connections.

    Raises:
        OperationalError: If a connection error occurs.

    Prints a success message if the connection is successful, or a failure message otherwise.
    """
    try:
        connection = engine.connect()
        print("Database connected successfully.")
        connection.close()
    except OperationalError:
        print("Failed to connect to the database.")


def check_table_exists(table_name: str, engine) -> None:
    """
    Checks if a specified table exists in the database and creates it if not.

    Args:
        table_name: The name of the table to check.
        engine: The SQLAlchemy engine object used for database connections.

    Prints messages indicating whether the table exists or needs to be created.
    """
    if engine.dialect.has_table(engine.connect(), table_name):
        print(f"Table '{table_name}' exists.")
    else:
        print(f"Table '{table_name}' does not exist.")
        print("Creating table...")
        create_database_tables()
        print(f"Table '{table_name}' created.")


def new_data_job() -> None:
    """
    Retrieves the highest existing ID in the database, uses it as a starting point
    to fetch new data from the BGG API.
    The retrieved new board game data is input it in the database.
    """
    last_id = get_highest_id()
    get_new_data(last_id)
