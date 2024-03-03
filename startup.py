from sqlalchemy.exc import OperationalError
from database import create_database_tables


def check_db_connection(engine) -> None:
    try:
        connection = engine.connect()
        print("Database connected successfully.")
        connection.close()
    except OperationalError:
        print("Failed to connect to the database.")


def check_table_exists(table_name: str, engine) -> None:
    if engine.dialect.has_table(engine.connect(), table_name):
        print(f"Table '{table_name}' exists.")
    else:
        print(f"Table '{table_name}' does not exist.")
        print("Creating table...")
        create_database_tables()
        print(f"Table '{table_name}' created.")
