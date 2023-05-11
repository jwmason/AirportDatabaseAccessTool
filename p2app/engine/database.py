"""This module is in charge of handling the database"""

import sqlite3
from p2app.events.database import DatabaseOpenedEvent, DatabaseOpenFailedEvent


def process_open_database_event(event):
    """This function opens the database file"""
    database_path = event.path()
    # Checks if it's a database file
    db_checker = is_sqlite_database(database_path)
    if db_checker:
        connection = sqlite3.connect(database_path, isolation_level = None)
        _quietly_execute_statement(connection, 'PRAGMA foreign_keys = ON;')
        yield DatabaseOpenedEvent(database_path)
    else:
        yield DatabaseOpenFailedEvent('The file selected is not a database file.')


def is_sqlite_database(database_path):
    """Checks if file is a database"""
    with open(database_path, "rb") as file:
        header = file.read(16)
        return header.startswith(b"SQLite format 3")


def _quietly_execute_statement(connection, statement):
    """Executes a statement quietly"""
    cursor = None
    try:
        # Execute a statement that we expect not to return any data.
        cursor = connection.execute(statement)
    finally:
        # When we get here, cursor might be None (if executing the statement
        # failed), so we need to be careful to close the cursor only if it
        # was opened.
        if cursor is not None:
            cursor.close()