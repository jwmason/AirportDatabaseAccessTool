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
from p2app.events.continents import StartContinentSearchEvent, ContinentSearchResultEvent
from collections import namedtuple


class Engine:
    """An object that represents the application's engine, whose main role is to
    process events sent to it by the user interface, then generate events that are
    sent back to the user interface in response, allowing the user interface to be
    unaware of any details of how the engine is implemented.
    """

    connection = None

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
            if db_checker:
                yield DatabaseOpenedEvent(database_path)
                global connection
                connection = sqlite3.connect(database_path, isolation_level = None)
                _quietly_execute_statement(connection, 'PRAGMA foreign_keys = ON;')
            else:
                yield DatabaseOpenFailedEvent('The file selected is not a database file.')

        elif type(event) == CloseDatabaseEvent:
            yield DatabaseClosedEvent()

        elif type(event) == StartContinentSearchEvent:
            continent_name = event._name
            continent_code = event._continent_code
            if continent_name is not None and event.continent_code is not None:
                # yield ContinentSearchResultEvent(continent)
                pass
            elif continent_name is not None:
                # yield ContinentSearchResultEvent(continent)
                pass
            elif event.continent_code is not None:
                cursor = connection.cursor()

                # Execute the SQL statement
                cursor.execute("SELECT * FROM continent WHERE continent_code = ?",
                               (continent_code,))

                # Fetch the result
                result = cursor.fetchone()
                Continent = namedtuple('Continent', ['continent_id', 'continent_code', 'name'])
                result = Continent._make(result)
                yield ContinentSearchResultEvent(result)
                # Close the cursor and the database connection
                cursor.close()


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