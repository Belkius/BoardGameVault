import requests
import xml.etree.ElementTree as ET
from database import Boardgame, insert_items_data, get_highest_id
import time



def parse_games_data(xml_data: object):
    items_data = {}
    root = ET.fromstring(xml_data)
    for boardgame in root.findall("item"):
        item_id = int(boardgame.get("id"))
        items_data[item_id] = {
            "item_id": item_id,
            "type": boardgame.get("type"),
            "name": get_value(boardgame, 'name[@type="primary"]'),
            "alternate_names": get_all_values_list(boardgame, "name", "alternate"),
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
    if value:
        try:
            return int(value)
        except ValueError:
            pass
    return -1


def value_to_float(value: str) -> float:
    if value:
        try:
            return float(value)
        except ValueError:
            pass
    return -1.0


def get_all_values_list(boardgame, tag_name: str, tag_type: str) -> list:
    all_values_list = []
    for tag in boardgame.findall(tag_name + f'[@type="{tag_type}"]'):
        all_values_list.append(tag.get("value"))
    return all_values_list


def get_value(element, tag_name):
    if element.find(tag_name) is not None:
        return element.find(tag_name).get("value")
    return -1


def get_api_data(game_id: str) -> str:
    base_url = "https://www.boardgamegeek.com/xmlapi2/thing"
    params = {
        "id": game_id,
        "stats": 1,
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as err:
        return f"HTTP Error: {err}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"


def get_new_data(last_item_id: int) -> dict:
    highest_id = last_item_id
    while True:
        item_ids = ",".join([str(id) for id in range(highest_id, highest_id + 100)])
        api_response = get_api_data(item_ids)
        items_data = parse_games_data(api_response)
        if not items_data:
            break
        highest_id += 100
        insert_items_data(items_data)
        keep_server_healthy(2)
    print("done")
    return items_data


def keep_server_healthy(seconds: int):
    time.sleep(seconds)
    # add more health checks here


# last_game_id = 414830
last_game_id = 412199
get_new_data(last_game_id)
print(get_highest_id())