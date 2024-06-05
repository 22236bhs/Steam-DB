'''Function library to interface with steam'''
import requests
import json, os
os.chdir("C:/Users/ojkit/Documents/Steam DB")
with open("data.json") as f:
    data = json.load(f)



# Note: data.json is a hidden json file containing the steam id and api key
# Format:  {"steam_id": "id", "api_key": "key"}
# Where "id" is replaced with the steam id and "key" is replaced with the api key 
API_KEY = data["api_key"]
steam_id = data["steam_id"]

months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
          "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
days = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08",
        "9": "09"}


def GetHours(game_ids):
    '''Takes the list argument of tuples [(id, game_id), ...]
       and returns a list of tuples [(id, hours), ...]'''
    global data, steam_id, API_KEY
    UpdateId()

    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steam_id}&format=json'
    try:
        response = requests.get(url)
    except:
        return 10

    if response.status_code == 200:
        try:
            data = response.json()
        except:
            return 12
        if 'response' in data and 'games' in data['response']:
                finallist = []
                for game in data['response']['games']:
                    for entry in game_ids:
                        if game['appid'] == entry[1]:
                            finallist.append((entry[0], round((game['playtime_forever'] / 60), 1)))
                return finallist
    else:
        return 11



def GetGameDetails(appid, language='english'):
    '''Returns the release date in two forms and the developer of the given appid'''
    global data, steam_id, API_KEY
    UpdateId()
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
        try:
            ConvertDate(release_date)
        except:
            return None
        else:
            return {
                'release_date': ConvertDate(release_date),
                'developer': developer[0],
            }
    return None

def ConvertDate(date):
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



def GetBasicData():
    '''Gets the appid, name and hours of the user's steam library'''
    global data, steam_id, API_KEY
    UpdateId()
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

    params = {
        'key': API_KEY,
        'steamid': steam_id,
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

def CompileData():
    '''Accesses the GetBasicData and GetGameDetails functions and combines their data'''
    basicdata = GetBasicData()
    if isinstance(basicdata, int):
        return basicdata
    if basicdata:
        blacklist = []
        for i in range(len(basicdata)):
            moredetails = GetGameDetails(basicdata[i]["appid"])
            if isinstance(moredetails, int):
                return moredetails
            if moredetails:
                basicdata[i]["release_date"] = moredetails["release_date"]
                basicdata[i]["developer"] = moredetails["developer"]
            else:
                blacklist.append(i)
        final = []
        for i in range(len(basicdata)):
            if i in blacklist:
                continue
            final.append(basicdata[i])
        return final
    else:
        return None

def TestId(id):
    global steam_id, data, API_KEY
    UpdateId()
    '''Tests if the argument is a valid steam id'''
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={id}&format=json'
    try:
        response = requests.get(url)
    except:
        return 10
    if response.status_code == 200:
        try:
            jsontest = response.json()
        except:
            return 12
        else:
            return True
    else:
        return False


def TestConnection():
    global steam_id, data, API_KEY
    UpdateId()
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steam_id}&format=json"
    try:
        response = requests.get(url)
    except ConnectionError:
        return False
    else:
        return True




def UpdateId():
    global steam_id, data
    with open('data.json') as f:
        data = json.load(f)
    steam_id = data["steam_id"]


if __name__ == "__main__":
    TestId(4)