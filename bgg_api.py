import requests
def get_game_info(game_id: str) -> str:
    base_url = "https://www.boardgamegeek.com/xmlapi2/thing"
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
        return f"HTTP Error: {err}"
    except requests.exceptions.RequestException as err:
        return f"Request Error: {err}"

print(get_game_info("1,2"))