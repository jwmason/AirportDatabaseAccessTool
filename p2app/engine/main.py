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
from p2app.events.continents import StartContinentSearchEvent, ContinentSearchResultEvent,\
    LoadContinentEvent, ContinentLoadedEvent, ContinentSavedEvent, SaveNewContinentEvent,\
    SaveContinentFailedEvent, SaveContinentEvent
from p2app.events.countries import StartCountrySearchEvent, CountrySearchResultEvent,\
    LoadCountryEvent, CountryLoadedEvent, SaveCountryEvent, SaveNewCountryEvent, CountrySavedEvent,\
    SaveCountryFailedEvent
from p2app.events.regions import StartRegionSearchEvent, RegionSearchResultEvent, LoadRegionEvent,\
    RegionLoadedEvent, SaveNewRegionEvent, SaveRegionEvent, RegionSavedEvent, SaveRegionFailedEvent
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

        # Defining global namedtuple variables
        define_globals()

        # Application-Level Events

        if isinstance(event, QuitInitiatedEvent):
            yield EndApplicationEvent()

        elif isinstance(event, OpenDatabaseEvent):
            yield from process_open_database_event(event)

        elif isinstance(event, CloseDatabaseEvent):
            yield DatabaseClosedEvent()

        # Continent-Related Events

        elif isinstance(event, StartContinentSearchEvent):
            yield from process_start_continent_search_event(event)

        elif isinstance(event, LoadContinentEvent):
            yield from process_load_continent_event(event)

        elif isinstance(event, (SaveNewContinentEvent, SaveContinentEvent)):
            yield from process_save_continent_event(event)

        # Country-related Events

        elif isinstance(event, StartCountrySearchEvent):
            yield from process_start_country_search_event(event)


        elif isinstance(event, LoadCountryEvent):
            yield from process_load_country_event(event)

        elif isinstance(event, (SaveNewCountryEvent, SaveCountryEvent)):
            yield from process_save_country_event(event)

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


def process_open_database_event(event):
    """This function opens the database file"""
    database_path = event.path()
    # Checks if it's a database file
    db_checker = is_sqlite_database(database_path)
    if db_checker:
        global connection
        # Allowing only one connection at a time and turning on data integrity
        connection = sqlite3.connect(database_path, isolation_level = None)
        _quietly_execute_statement(connection, 'PRAGMA foreign_keys = ON;')
        yield DatabaseOpenedEvent(database_path)
    else:
        yield DatabaseOpenFailedEvent('The file selected is not a database file.')


def process_start_continent_search_event(event):
    """This function starts continent search"""
    # Defining parameters
    continent_name = event._name
    continent_code = event._continent_code
    cursor = connection.cursor()
    # Checking all cases of search parameters
    if continent_name is not None and continent_code is not None:
        cursor.execute("SELECT * FROM continent WHERE continent_code = ? AND name = ?;",
                       (continent_code, continent_name))
    elif continent_name is not None:
        cursor.execute("SELECT * FROM continent WHERE name = ?;",
                       (continent_name,))
    elif continent_code is not None:
        cursor.execute("SELECT * FROM continent WHERE continent_code = ?;",
                       (continent_code,))
    # Fetching result
    result = cursor.fetchall()
    if result is not None:
        for continent in result:
            continent = Continent._make(continent)
            yield ContinentSearchResultEvent(continent)
    else:
        yield ()
    cursor.close()


def process_load_continent_event(event):
    """This function loads continent based on id"""
    # Defining parameters
    continent_id = event._continent_id
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM continent WHERE continent_id = ?;",
                   (continent_id,))
    # Fetching result
    result = cursor.fetchone()
    if result is not None:
        result = Continent._make(result)
        yield ContinentLoadedEvent(result)
    else:
        yield ()
    cursor.close()


def process_save_continent_event(event):
    """This function saves continent information, old and new continents"""
    # Defining parameters
    continent = event._continent
    continent_id = continent.continent_id
    continent_code = continent.continent_code
    name = continent.name
    cursor = connection.cursor()

    # Filtering New Continent Event versus Existing Continent Event
    try:
        if isinstance(event, SaveNewContinentEvent):
            cursor.execute(
                "INSERT INTO continent (continent_id, continent_code, name) VALUES (?, ?, ?);",
                (continent_id, continent_code, name))
        elif isinstance(event, SaveContinentEvent):
            cursor.execute(
                "UPDATE continent SET continent_code = ?, name = ? WHERE continent_id = ?;",
                (continent_code, name, continent_id))
    except sqlite3.IntegrityError as e:
        yield SaveContinentFailedEvent(e)
    # Fetching result
    result = cursor.fetchone()
    yield ContinentSavedEvent(result)
    cursor.close()


def process_start_country_search_event(event):
    """This function starts a country search"""
    # Defining parameters
    country_name = event._name
    country_code = event._country_code
    cursor = connection.cursor()

    # Checking all cases of search parameters
    if country_name is not None and country_code is not None:
        cursor.execute("SELECT * FROM country WHERE country_code = ? AND name = ?;",
                       (country_code, country_name))
    elif country_name is not None:
        cursor.execute("SELECT * FROM country WHERE name = ?;",
                       (country_name,))
    elif country_code is not None:
        cursor.execute("SELECT * FROM country WHERE country_code = ?;",
                       (country_code,))
        # Fetching result
        result = cursor.fetchall()
        if result is not None:
            for country in result:
                country = Country._make(country)
                yield RegionSearchResultEvent(country)
        else:
            yield ()
        cursor.close()


def process_load_country_event(event):
    """This function loads country based on id"""
    # Defining parameters
    country_id = event._country_id
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM country WHERE country_id = ?;",
                   (country_id,))
    # Fetching result
    result = cursor.fetchone()
    if result is not None:
        result = Country._make(result)
        yield CountryLoadedEvent(result)
    else:
        yield ()
    cursor.close()


def process_save_country_event(event):
    """This function saves country information, old and new countries"""
    # Defining parameters
    country = event._country
    country_id = country.country_id
    country_code = country.country_code
    name = country.name
    continent_id = country.continent_id
    wiki_link = country.wikipedia_link
    keywords = country.keywords
    cursor = connection.cursor()
    # Filtering New Country Event versus Existing Country Event
    try:
        if isinstance(event, SaveNewCountryEvent):
            cursor.execute(
                "INSERT INTO country (country_id, country_code, name, continent_id, wikipedia_link, keywords) VALUES (?, ?, ?, ?, ?, ?);",
                (country_id, country_code, name, continent_id, wiki_link, keywords))
        elif isinstance(event, SaveCountryEvent):
            cursor.execute(
                "UPDATE country SET country_code = ?, name = ?, continent_id = ?, wikipedia_link = ?, keywords = ? WHERE country_id = ?;",
                (country_code, name, continent_id, wiki_link, keywords, country_id))
    except sqlite3.IntegrityError as e:
        yield SaveCountryFailedEvent(e)
    # Fetching result
    result = cursor.fetchone()
    yield CountrySavedEvent(result)
    cursor.close()


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
    pass


def process_save_region_event(event):
    pass


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
