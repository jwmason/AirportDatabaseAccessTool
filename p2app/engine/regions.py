"""This module is in charge of handling region functions"""


import sqlite3
from p2app.events.regions import RegionSearchResultEvent, RegionLoadedEvent, SaveNewRegionEvent,\
    SaveRegionEvent, RegionSavedEvent, SaveRegionFailedEvent
from collections import namedtuple

def define_globals():
    """This function defines the global namedtuples of the functions"""
    global Region
    Region = namedtuple('Region', ['region_id', 'region_code', 'local_code', 'name',
                                   'continent_id', 'country_id', 'wikipedia_link', 'keywords'])


def process_start_region_search_event(event, connection):
    """This function starts region search event"""
    # Defining parameters
    define_globals()
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


def process_load_region_event(event, connection):
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


def process_save_region_event(event, connection):
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
