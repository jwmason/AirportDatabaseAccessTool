"""This module is in charge of handling all continent functions"""


import sqlite3
from p2app.events.continents import ContinentSearchResultEvent, ContinentLoadedEvent, SaveContinentEvent,\
    SaveContinentFailedEvent, SaveNewContinentEvent, ContinentSavedEvent
from collections import namedtuple


def define_globals():
    """This function defines the global namedtuples of the functions"""
    global Continent
    Continent = namedtuple('Continent', ['continent_id', 'continent_code', 'name'])


def process_start_continent_search_event(event, connection):
    """This function starts continent search"""
    # Defining parameters
    define_globals()
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


def process_load_continent_event(event, connection):
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


def process_save_continent_event(event, connection):
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
    else:
        # Fetching result
        result = cursor.fetchone()
        yield ContinentSavedEvent(result)
    cursor.close()
