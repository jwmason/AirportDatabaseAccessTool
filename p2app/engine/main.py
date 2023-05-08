# p2app/engine/main.py
#
# ICS 33 Spring 2023
# Project 2: Learning to Fly
#
# An object that represents the engine of the application.
#
# This is the outermost layer of the part of the program that you'll need to build,
# which means that YOU WILL DEFINITELY NEED TO MAKE CHANGES TO THIS FILE.


import sqlite3
from p2app.events.app import QuitInitiatedEvent, EndApplicationEvent
from p2app.events.database import OpenDatabaseEvent, CloseDatabaseEvent,\
    DatabaseOpenedEvent, DatabaseOpenFailedEvent, DatabaseClosedEvent


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    def __init__(self):
        """Initializes the engine"""
        pass


    def process_event(self, event):
        """A generator function that processes one event sent from the user interface,
        yielding zero or more events in response."""

        # This is a way to write a generator function that always yields zero values.
        # You'll want to remove this and replace it with your own code, once you start
        # writing your engine, but this at least allows the program to run.
        if type(event) == QuitInitiatedEvent:
            yield EndApplicationEvent()

        elif type(event) == OpenDatabaseEvent:
            database_path = event.path()
            db_checker = is_sqlite_database(database_path)
            try:
                if db_checker:
                    connection = sqlite3.connect(database_path, isolation_level = None)
                    _quietly_execute_statement(connection, 'PRAGMA foreign_keys = ON;')
                    yield DatabaseOpenedEvent(database_path)
                else:
                    yield DatabaseOpenFailedEvent('not a database')
            except sqlite3.Error as e:
                _display_error(e)

        elif type(event) == CloseDatabaseEvent:
            yield DatabaseClosedEvent()

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


def _display_error(e):
    error_message = ' '.join(e.args)
    print(f'ERROR: {error_message}')