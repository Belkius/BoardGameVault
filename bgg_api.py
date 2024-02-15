import requests
import xml.etree.ElementTree as ET
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import psycopg2
from database import Boardgame
import html


# convert=html.unescape()


def parse_games_data(xml_data: object):
    items_data = {}
    root = ET.fromstring(xml_data)
    for boardgame in root.findall("item"):
        item_id = int(boardgame.get("id"))
        items_data[item_id] = {
            "item_id": item_id,
            "type": boardgame.get("type"),
            "name": boardgame.find('name[@type="primary"]').get("value"),
            "alternate_names": get_all_values_list(boardgame, "name", "alternate"),
            "description": boardgame.find("description").text,
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
            "users_rated": get_value(boardgame, "statistics/ratings/usersrated"),
            "average_rating": get_value(boardgame, "statistics/ratings/average"),
            "bayes_average": get_value(boardgame, "statistics/ratings/bayesaverage"),
            "bgg_rank": get_value(
                boardgame, 'statistics/ratings/ranks/rank[@type="subtype"]'
            ),
            "num_weights": get_value(boardgame, "statistics/ratings/numweights"),
            "average_weight": get_value(boardgame, "statistics/ratings/averageweight"),
            "thumbnail": boardgame.find("thumbnail").text,
            "image": boardgame.find("image").text,
        }
    return items_data


def get_all_values_list(boardgame, tag_name: str, type: str) -> list:
    all_values_list = []
    for tag in boardgame.findall(tag_name + f'[@type="{type}"]'):
        all_values_list.append(tag.get("value"))
    return all_values_list


def get_value(element, tag_name):
    try:
        return element.find(tag_name).get("value")
    except:
        return None


def insert_items_data(session, items_data):
    for id, data in items_data.items():
        existing_game = session.query(Boardgame).filter_by(item_id=id).first()
        if not existing_game:
            new_game = Boardgame(**data)
            session.add(new_game)
    session.commit()


def get_api_data(game_id: str) -> str:
    base_url = "https://www.boardgamegeek.com/xmlapi2/thing"
    params = {
        "id": game_id,
        "stats": 1,  # Include game statistics
    }

    response = requests.get(base_url, params=params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses

        return response.text
    except requests.exceptions.HTTPError as err:
        return f"HTTP Error: {err}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"


game_ids = "1,2,3,10,24,23,231,231,213,132,21,3,2,23,32,4,543,4,5,356,3"  # Replace with desired IDs or retrieve dynamically
api_response = get_api_data(game_ids)
items_data = parse_games_data(api_response)
print(items_data)
session = SessionLocal()
try:
    insert_items_data(session, items_data)
finally:
    session.close()


# print(root[0][1].text)
# for child in root:
#     print(child.tag, child.attrib)

# for boardgame in root.findall('item'):
#     print(boardgame.get('id'), boardgame.find('name').get('value'))
# print(get_api_data(z))
