def gethours(game_ids):
    '''Takes the list argument of tuples [(id, game_id), ...] and returns a list [(id, hours), ...]'''
    import requests
    import json

    # Note: data.json is a hidden json file containing the steam id and api key
    # Format:  {"steam_id": "id", "api_key": "key"}

    with open("data.json") as f:
        data = json.load(f)
    
    API_KEY = data["api_key"]
    STEAM_ID = data["steam_id"]

    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        if 'response' in data and 'games' in data['response']:
                finallist = []
                for game in data['response']['games']:
                    for entry in game_ids:
                        if game['appid'] == entry[1]:
                            finallist.append((entry[0], round((game['playtime_forever'] / 60), 1)))
                return finallist
    else:
        return False
        