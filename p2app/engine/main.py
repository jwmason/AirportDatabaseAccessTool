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
from p2app.events.app import QuitInitiatedEvent, EndApplicationEvent, ErrorEvent
from p2app.events.database import OpenDatabaseEvent, CloseDatabaseEvent, DatabaseClosedEvent
from p2app.events.continents import StartContinentSearchEvent, ContinentSearchResultEvent,\
    LoadContinentEvent, ContinentLoadedEvent, ContinentSavedEvent, SaveNewContinentEvent,\
    SaveContinentFailedEvent, SaveContinentEvent
from p2app.events.countries import StartCountrySearchEvent, CountrySearchResultEvent,\
    LoadCountryEvent, CountryLoadedEvent, SaveCountryEvent, SaveNewCountryEvent, CountrySavedEvent,\
    SaveCountryFailedEvent
from p2app.events.regions import StartRegionSearchEvent, RegionSearchResultEvent, LoadRegionEvent,\
    RegionLoadedEvent, SaveNewRegionEvent, SaveRegionEvent, RegionSavedEvent, SaveRegionFailedEvent

# p2app.engine modules

from p2app.engine.database import process_open_database_event, is_sqlite_database
from p2app.engine.continents import process_start_continent_search_event,\
    process_load_continent_event, process_save_continent_event
from p2app.engine.countries import process_start_country_search_event, process_load_country_event,\
    process_save_country_event

# Continent, Country, Region naming

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
            yield from process_start_region_search_event(event)

        elif isinstance(event, LoadRegionEvent):
            yield from process_load_region_event(event)

        elif isinstance(event, (SaveNewRegionEvent, SaveRegionEvent)):
            yield from process_save_region_event(event)


def define_globals():
    """This function defines the global namedtuples of the functions"""
    global Continent
    Continent = namedtuple('Continent', ['continent_id', 'continent_code', 'name'])
    global Country
    Country = namedtuple('Country', ['country_id', 'country_code', 'name', 'continent_id',
                                     'wikipedia_link', 'keywords'])
    global Region
    Region = namedtuple('Region', ['region_id', 'region_code', 'local_code', 'name',
                                   'continent_id', 'country_id', 'wikipedia_link', 'keywords'])


def get_connection(event):
    database_path = event.path()
    # Checks if it's a database file
    db_checker = is_sqlite_database(database_path)
    if db_checker:
        # Allowing only one connection at a time and turning on data integrity
        connection = sqlite3.connect(database_path, isolation_level = None)
    return connection


def process_start_region_search_event(event):
    """This function starts region search event"""
    # Defining parameters
    region_name = event._name
    region_code = event._region_code
    region_local_code = event._local_code
    cursor = connection.cursor()
    # Checking all cases of search parameters
    if region_name is not None and region_code is not None and region_local_code is not None:
        cursor.execute("SELECT * FROM region WHERE region_code = ? AND name = ? AND local_code = ?;",
                       (region_code, region_name, region_local_code))
    elif region_name is not None and region_code is not None:
        cursor.execute("SELECT * FROM region WHERE region_code = ? AND name = ?;",
                       (region_code, region_name,))
    elif region_name is not None and region_local_code is not None:
        cursor.execute("SELECT * FROM region WHERE local_code = ? AND name = ?;",
                       (region_local_code, region_name,))
    elif region_code is not None and region_local_code is not None:
        cursor.execute("SELECT * FROM region WHERE local_code = ? AND region_code = ?;",
                       (region_local_code, region_code,))
    elif region_name is not None:
        cursor.execute("SELECT * FROM region WHERE name = ?;",
                       (region_name,))
    elif region_code is not None:
        cursor.execute("SELECT * FROM region WHERE region_code = ?;",
                       (region_code,))
    elif region_local_code is not None:
        cursor.execute("SELECT * FROM region WHERE local_code = ?;",
                       (region_local_code,))
    # Fetching result
    result = cursor.fetchall()
    if result is not None:
        for region in result:
            region = Region._make(region)
            yield RegionSearchResultEvent(region)
    else:
        yield ()
    cursor.close()


def process_load_region_event(event):
    """This function loads region based on id"""
    # Defining parameters
    region_id = event._region_id
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM region WHERE region_id = ?;",
                   (region_id,))
    # Fetching result
    result = cursor.fetchone()
    if result is not None:
        result = Region._make(result)
        yield RegionLoadedEvent(result)
    else:
        yield ()
    cursor.close()


def process_save_region_event(event):
    """This function saves region information, old and new regions"""
    # Defining parameters
    region = event._region
    region_id = region.region_id
    region_code = region.region_code
    local_code = region.local_code
    name = region.name
    continent_id = region.continent_id
    country_id = region.country_id
    wikipedia_link = region.wikipedia_link
    keywords = region.keywords
    cursor = connection.cursor()
    # Filtering New Country Event versus Existing Country Event
    try:
        if isinstance(event, SaveNewRegionEvent):
            cursor.execute(
                "INSERT INTO region (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
                (region_id, region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords))
        elif isinstance(event, SaveRegionEvent):
            cursor.execute(
                "UPDATE region SET region_code = ?, local_code = ?, name = ?, continent_id = ?, country_id = ?, wikipedia_link = ?, keywords = ? WHERE region_id = ?;",
                (region_code, local_code, name, continent_id, country_id, wikipedia_link, keywords, region_id))
    except sqlite3.IntegrityError as e:
        yield SaveRegionFailedEvent(e)
    # Fetching result
    result = cursor.fetchone()
    yield RegionSavedEvent(result)
    cursor.close()
