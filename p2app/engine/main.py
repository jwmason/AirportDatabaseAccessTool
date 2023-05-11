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

# p2app.event modules

from p2app.events.app import QuitInitiatedEvent, EndApplicationEvent, ErrorEvent
from p2app.events.database import OpenDatabaseEvent, CloseDatabaseEvent, DatabaseClosedEvent
from p2app.events.continents import StartContinentSearchEvent, LoadContinentEvent, SaveNewContinentEvent,SaveContinentEvent
from p2app.events.countries import StartCountrySearchEvent, LoadCountryEvent, SaveCountryEvent, SaveNewCountryEvent
from p2app.events.regions import StartRegionSearchEvent, LoadRegionEvent, SaveNewRegionEvent, SaveRegionEvent

# p2app.engine modules

from p2app.engine.database import process_open_database_event, is_sqlite_database
from p2app.engine.continents import process_start_continent_search_event,\
    process_load_continent_event, process_save_continent_event
from p2app.engine.countries import process_start_country_search_event, process_load_country_event,\
    process_save_country_event
from p2app.engine.regions import process_start_region_search_event, process_load_region_event,\
    process_save_region_event


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

        # Application-Level Events

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()
        elif isinstance(event, OpenDatabaseEvent):
            # Making connection to database global
            yield from process_open_database_event(event)
            try:
                global connection
                connection = get_connection(event)
            except UnboundLocalError:
                pass
        elif isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent()

        # Continent-Related Events

        elif isinstance(event, StartContinentSearchEvent):
            yield from process_start_continent_search_event(event, connection)
        elif isinstance(event, LoadContinentEvent):
            yield from process_load_continent_event(event, connection)
        elif isinstance(event, (SaveNewContinentEvent, SaveContinentEvent)):
            yield from process_save_continent_event(event, connection)

        # Country-related Events

        elif isinstance(event, StartCountrySearchEvent):
            yield from process_start_country_search_event(event, connection)
        elif isinstance(event, LoadCountryEvent):
            yield from process_load_country_event(event, connection)
        elif isinstance(event, (SaveNewCountryEvent, SaveCountryEvent)):
            yield from process_save_country_event(event, connection)

        # Region-related Events

        elif isinstance(event, StartRegionSearchEvent):
            yield from process_start_region_search_event(event, connection)
        elif isinstance(event, LoadRegionEvent):
            yield from process_load_region_event(event, connection)
        elif isinstance(event, (SaveNewRegionEvent, SaveRegionEvent)):
            yield from process_save_region_event(event, connection)


def get_connection(event):
    database_path = event.path()
    # Checks if it's a database file
    db_checker = is_sqlite_database(database_path)
    if db_checker:
        # Allowing only one connection at a time and turning on data integrity
        connection = sqlite3.connect(database_path, isolation_level = None)
    return connection
