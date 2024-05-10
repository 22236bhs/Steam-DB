def gethours(YOUR_GAME_APP_ID):
    import requests
    import json

    # Note: data.json is a hidden json file containing the steam id and api key
    # Format:  {"steam_id": "id", "api_key": "key"}

    with open("data.json") as f:
        data = json.load(f)
    
    API_KEY = data["api_key"]
    STEAM_ID = data["steam_id"]

    # URL for the GetOwnedGames API endpoint
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json'

    # Make the HTTP request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Check if the response contains the playtime data
        if 'response' in data and 'games' in data['response']:
            # Iterate over the games and find the one you're interested in
            for game in data['response']['games']:
                if game['appid'] == YOUR_GAME_APP_ID:
                    return (game['playtime_forever'] / 60)
    else:
        return False
        
