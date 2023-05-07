"""This module is in charge of handling application-level events"""

import sqlite3
from p2app.events.database import DatabaseOpenedEvent, DatabaseOpenFailedEvent, DatabaseClosedEvent


def opendatabaseevent(event):
    """function attempts to connect to database"""
    database_path = event.path()
    connection = None

    try:
        connection = _connect(database_path)
        yield DatabaseOpenedEvent

    except sqlite3.Error as e:
        print('Error:', e)
        yield DatabaseOpenFailedEvent


def _disconnect(connection):
    if connection is not None:
        connection.close()
        yield DatabaseClosedEvent


def _connect(database_path):
    # The "isolation_level" parameter is a way of controlling what
    # happens when more than one connection modifies the database
    # simultaneously, which is a problem we won't need to address
    # here, so our best bet is to simply turn that feature off.
    connection = sqlite3.connect(database_path, isolation_level = None)

    # Ask SQLite to enforce foreign keys, which is not the default, so
    # we have to turn this feature on each time we connect.
    _quietly_execute_statement(connection, 'PRAGMA foreign_keys = ON;')

    return connection


def _quietly_execute_statement(connection, statement):
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