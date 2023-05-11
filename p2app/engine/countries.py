"""This module is in charge of handling countries"""


import sqlite3
from p2app.events.countries import CountrySearchResultEvent, CountryLoadedEvent,\
    SaveNewCountryEvent, SaveCountryEvent, CountrySavedEvent, SaveCountryFailedEvent
from collections import namedtuple


def define_globals():
    """This function defines the global namedtuples of the functions"""
    global Country
    Country = namedtuple('Country', ['country_id', 'country_code', 'name', 'continent_id',
                                     'wikipedia_link', 'keywords'])


def process_start_country_search_event(event, connection):
    """This function starts a country search"""
    # Defining parameters
    define_globals()
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
                yield CountrySearchResultEvent(country)
        else:
            yield ()
        cursor.close()


def process_load_country_event(event, connection):
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


def process_save_country_event(event, connection):
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
    else:
        # Fetching result
        result = cursor.fetchone()
        yield CountrySavedEvent(result)
    cursor.close()
