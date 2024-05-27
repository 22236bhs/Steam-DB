'''Function library to interface with steam'''
import requests
import json, os
with open("data.json") as f:
    data = json.load(f)

os.chdir("C:/Users/ojkit/Documents/Steam DB")

# Note: data.json is a hidden json file containing the steam id and api key
# Format:  {"steam_id": "id", "api_key": "key"}
# Where "id" is replaced with the steam id and "key" is replaced with the api key 
API_KEY = data["api_key"]
STEAM_ID = data["steam_id"]

months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
          "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
days = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08",
        "9": "09"}


def gethours(game_ids):
    global data, STEAM_ID, API_KEY
    with open("data.json") as f:
        data = json.load(f)
    STEAM_ID = data["steam_id"]
    API_KEY = data["api_key"]
    '''Takes the list argument of tuples [(id, game_id), ...]
       and returns a list of tuples [(id, hours), ...]'''
    


    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json'
    try:
        response = requests.get(url)
    except:
        return 10

    if response.status_code == 200:
        try:
            data = response.json()
        except:
            return 11
        
        if 'response' in data and 'games' in data['response']:
                finallist = []
                for game in data['response']['games']:
                    for entry in game_ids:
                        if game['appid'] == entry[1]:
                            finallist.append((entry[0], round((game['playtime_forever'] / 60), 1)))
                return finallist
    else:
        return 12



def get_game_details(appid, language='english'):
    global data, STEAM_ID, API_KEY
    with open("data.json") as f:
        data = json.load(f)
    STEAM_ID = data["steam_id"]
    API_KEY = data["api_key"]
    '''Returns the release date in two forms and the developer of the given appid'''
    url = f'https://store.steampowered.com/api/appdetails'
    params = {
        'appids': appid,
        'cc': 'us',  
        'l': language  
    }
    try:
        response = requests.get(url, params=params)
    except:
        return 10
    try:
        data = response.json()
    except:
        return 11
    if str(appid) in data and data[str(appid)]['success']:
        details = data[str(appid)]['data']
        release_date = details.get('release_date', {}).get('date')
        developer = details.get('developers', [])
        
        return {
            'release_date': convertdate(release_date),
            'developer': developer[0],
        }
    return None

def convertdate(date):
    '''Converts month day, year to a tuple containing (dd/mm/yyyy, yyyymmdd)'''
    date = date.replace(",", "")
    date = date.split()
    date = [date[1], date[0], date[2]]
    date[1] = months[(date[1].lower())]
    if date[0] in days:
        date[0] = days[date[0]]
    strdate = "/".join(date)
    intdate = int(date[2] + date[1] + date[0])
    return {"strdate": strdate, "intdate": intdate}



def getbasicdata():
    '''Gets the appid, name and hours of the user's steam library'''
    global data, STEAM_ID, API_KEY
    with open("data.json") as f:
        data = json.load(f)
    STEAM_ID = data["steam_id"]
    API_KEY = data["api_key"]
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

    params = {
        'key': API_KEY,
        'steamid': STEAM_ID,
        'format': 'json',
        'include_appinfo': True,  
        'include_played_free_games': True  
    }
    try:
        response = requests.get(url, params=params)
    except:
        return 10
    try:
        data = response.json()
    except:
        return 11

    if 'response' in data and 'games' in data['response']:
        games = data['response']['games']
        list = []
        for game in games:
            tup = {}
            appid = game.get('appid')
            name = game.get('name')
            playtime_forever = game.get('playtime_forever')
            
            playtime_forever = round((playtime_forever / 60), 1)
            if playtime_forever >= 1:
                tup["appid"] = appid
                tup["name"] = name
                tup["playtime"] = playtime_forever
                list.append(tup)
        return list
                
    else:
        return None

def compiledata():
    '''Accesses the getbasicdata and get_game_details functions and combines their data'''
    basicdata = getbasicdata()
    if basicdata:
        for i in range(len(basicdata)):
            moredetails = get_game_details(basicdata[i]["appid"])
            basicdata[i]["release_date"] = moredetails["release_date"]
            basicdata[i]["developer"] = moredetails["developer"]
        return basicdata
    else:
        return None

def testid(id):
    global STEAM_ID, data, API_KEY
    with open("data.json") as f:
        data = json.load(f)
    STEAM_ID = data["steam_id"]
    API_KEY = data["api_key"]
    '''Tests if the argument is a valid steam id'''
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={id}&format=json'
    try:
        response = requests.get(url)
    except:
        return 10
    if response.status_code == 200:
        return True
    else:
        return False


def testconnection():
    global STEAM_ID, data, API_KEY
    with open("data.json") as f:
        data = json.load(f)
    STEAM_ID = data["steam_id"]
    API_KEY = data["api_key"]
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={STEAM_ID}&format=json"
    try:
        response = requests.get(url)
    except ConnectionError:
        return False
    else:
        return True

