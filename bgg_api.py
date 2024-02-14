import requests
import xml.etree.ElementTree as ET
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import psycopg2
from database import Boardgame
import html
def parse_game_data(xml_data):
    game_data = {}
    root = ET.fromstring(xml_data)
    for boardgame in root.findall('item'):
        objectid = int(boardgame.get('id'))
        print(boardgame.tag)
        for description in boardgame.findall('thumbnail'):
            print(description.text)
        game_data[objectid] = {
            'objectid': objectid,
            'type': boardgame.get('type'),
            'name': boardgame.find('name[@type="primary"]').get('value'),
            'alternate_names': [],
            'description': boardgame.find('description').text,
            'yearpublished': get_data(boardgame, 'yearpublished'),
            'minplayers': get_data(boardgame, 'minplayers'),
            'maxplayers': get_data(boardgame, 'maxplayers'),
            'thumbnail': get_data(boardgame, 'thumbnail')

        }
        for alternate_name in boardgame.findall('name[@type="alternate"]'):
            game_data[objectid]['alternate_names'].append(alternate_name.get('value'))


    return game_data


def get_data(element, tag_name):
    try:
        return element.find(tag_name).get('value')
    except (AttributeError, TypeError):
        return None

def insert_game_data(session, game_data):
    for objectid, data in game_data.items():
        new_game = Boardgame(**data)
        session.add(new_game)
    session.commit()

def get_games_info(game_id: str) -> str:
    base_url = 'https://www.boardgamegeek.com/xmlapi2/thing'
    params = {
        'id': game_id,
        'stats': 1,  # Include game statistics
    }

    response = requests.get(base_url, params=params)

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises HTTPError for bad responses

        return response.text
    except requests.exceptions.HTTPError as err:
        return f'HTTP Error: {err}'
    except requests.exceptions.RequestException as err:
        return f'Request Error: {err}'


# iii = '1,2,3'
# jjj = get_games_info(iii)
# jjjj = ET.fromstring(jjj)
# for k in jjjj:
#     print(k.find("description").text.strip())
def parse_games_info(api_response: str):
    xml_tree = ET.fromstring(api_response)

    for item in xml_tree.findall('item'):
        print(item.get('id'), item.find('name').get('value'))

game_ids = '1, 2, 3'  # Replace with desired IDs or retrieve dynamically
api_response = get_games_info(game_ids)
game_data = parse_game_data(api_response)
print(game_data)
# session = SessionLocal()
# try:
#     insert_game_data(session, game_data)
# finally:
#     session.close()

# y = []
# for x in range(1, 100):
#     y.append(str(x))
# z = ','.join(y)
# print(z)
#
# z = '1, 2'
#
# api_response = get_games_info(z)
#
# post_games_info(api_response)
# root = ET.fromstring(get_games_info(z))

# print(root[0][1].text)
# for child in root:
#     print(child.tag, child.attrib)

# for boardgame in root.findall('item'):
#     print(boardgame.get('id'), boardgame.find('name').get('value'))
# print(get_games_info(z))
