import requests
import xml.etree.ElementTree as ET
from database import insert_items_data, get_highest_id
from typing import Union
import time


def parse_games_data(xml_data: object):
    """
    Parses XML data containing board game information into a dictionary.

    Args:
        xml_data: The XML data to be parsed.

    Returns:
        A dictionary with item IDs as keys and dictionaries containing
        parsed item data as values.
    """
    items_data = {}
    root = ET.fromstring(xml_data)
    for boardgame in root.findall("item"):
        item_id = int(boardgame.get("id"))
        items_data[item_id] = {
            "item_id": item_id,
            "type": boardgame.get("type"),
            "name": get_value(boardgame, 'name[@type="primary"]'),
            "alternate_names": get_all_values_list(boardgame, "name", "alternate"),
            "owned": False,
            "times_played": 0,
            "dates_played": "",
            "comments": "",
            "description": "",
            "yearpublished": get_value(boardgame, "yearpublished"),
            "minplayers": get_value(boardgame, "minplayers"),
            "maxplayers": get_value(boardgame, "maxplayers"),
            "playingtime": get_value(boardgame, "playingtime"),
            "minplaytime": get_value(boardgame, "minplaytime"),
            "maxplaytime": get_value(boardgame, "maxplaytime"),
            "age": get_value(boardgame, "minage"),
            "categories": get_all_values_list(boardgame, "link", "boardgamecategory"),
            "mechanics": get_all_values_list(boardgame, "link", "boardgamemechanic"),
            "families": get_all_values_list(boardgame, "link", "boardgamefamily"),
            "integrations": get_all_values_list(
                boardgame, "link", "boardgameintegration"
            ),
            "implementations": get_all_values_list(
                boardgame, "link", "boardgameimplementation"
            ),
            "designers": get_all_values_list(boardgame, "link", "boardgamedesigner"),
            "artists": get_all_values_list(boardgame, "link", "boardgameartist"),
            "publishers": get_all_values_list(boardgame, "link", "boardgamepublisher"),
            "users_rated": value_to_int(
                get_value(boardgame, "statistics/ratings/usersrated")
            ),
            "average_rating": value_to_float(
                get_value(boardgame, "statistics/ratings/average")
            ),
            "bayes_average": value_to_float(
                get_value(boardgame, "statistics/ratings/bayesaverage")
            ),
            "bgg_rank": value_to_int(
                get_value(boardgame, 'statistics/ratings/ranks/rank[@type="subtype"]')
            ),
            "num_weights": value_to_int(
                get_value(boardgame, "statistics/ratings/numweights")
            ),
            "average_weight": value_to_float(
                get_value(boardgame, "statistics/ratings/averageweight")
            ),
            "thumbnail": "",
            "image": "",
        }
        if boardgame.find("description") is not None:
            items_data[item_id]["description"] = boardgame.find("description").text
        if boardgame.find("thumbnail") is not None:
            items_data[item_id]["thumbnail"] = boardgame.find("thumbnail").text
        if boardgame.find("image") is not None:
            items_data[item_id]["image"] = boardgame.find("image").text
    return items_data


def value_to_int(value: str) -> int:
    """
    Attempts to convert a string value to an integer.

    Args:
        value: The string value to convert.

    Returns:
        The integer value if conversion is successful, otherwise -1.
    """
    if value:
        try:
            return int(value)
        except ValueError:
            pass
    return -1


def value_to_float(value: str) -> float:
    """
    Attempts to convert a string value to a float.

    Args:
        value: The string value to convert.

    Returns:
        The float value if conversion is successful, otherwise -1.0.
    """
    if value:
        try:
            return float(value)
        except ValueError:
            pass
    return -1.0


def get_all_values_list(boardgame: ET.Element, tag_name: str, tag_type: str) -> list:
    """
    Retrieves a list of values from XML elements matching a specific tag name and type.

    Args:
        boardgame: The root XML element to search within.
        tag_name: The name of the tags to search for.
        tag_type: The type attribute value to match for the tags.

    Returns:
        A list of the values found in the matching tags.
    """
    all_values_list = []
    for tag in boardgame.findall(tag_name + f'[@type="{tag_type}"]'):
        all_values_list.append(tag.get("value"))
    return all_values_list


def get_value(element: ET.Element, tag_name: str) -> Union[str, int]:
    """
    Retrieves the value of a specific tag within an XML element.

    Args:
        element: The XML element to search within.
        tag_name: The name of the tag to retrieve the value from.

    Returns:
        The value of the tag, or -1 if the tag is not found.
    """
    if element.find(tag_name) is not None:
        return element.find(tag_name).get("value")
    return -1


def get_api_data(game_id: str) -> str:
    """
    Fetches data from the BoardGameGeek XML API with retry logic.

    Args:
        game_id: The IDs of the games to fetch data for.

    Returns:
        The XML response text from the API.
    """
    base_url = "https://www.boardgamegeek.com/xmlapi2/thing"
    params = {
        "id": game_id,
        "stats": 1,
    }

    while True:
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            return response.text
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}. Retrying...")
            keep_server_healthy(0.2)
        except requests.exceptions.RequestException as err:
            print(f"Request Error: {err}. Retrying...")
            keep_server_healthy(0.2)


def get_new_data(last_item_id: int) -> dict:
    """
    Retrieves new board game data from the BGG API in chunks and stores it in the database.

    Args:
        last_item_id: The highest existing item ID in the database.

    Returns:
        A dictionary containing the parsed data of the newly downloaded items.
    """
    highest_id = last_item_id
    print(f"Downloading new items from item id {highest_id}.")
    while True:
        item_ids = ",".join([str(id) for id in range(highest_id, highest_id + 100)])
        api_response = get_api_data(item_ids)
        items_data = parse_games_data(api_response)
        if not items_data:
            break
        print(
            f"----Downloaded items from item id {highest_id} to {highest_id + 100}----"
        )
        highest_id += 100
        insert_items_data(items_data)
        keep_server_healthy(0.2)
    print("Downloaded all new items.")
    return items_data


def keep_server_healthy(seconds: int):
    """
    Introduces a delay for server health and potentially calls health checks.

    Args:
        seconds: The number of seconds to delay.
    """
    time.sleep(seconds)
    # add more health checks here
