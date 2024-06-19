'''Function library to interface with steam'''
import requests, json

#Load the json file into a variable
with open("data.json") as f:
    data = json.load(f)



# Note: data.json is a hidden json file containing the steam id and api key
# Format:  {"steam_id": "id", "api_key": "key"}
# Where "id" is replaced with the steam id and "key" is replaced with the api key 
API_KEY = data["api_key"]
steamId = data["steam_id"]

#Assign each month abbreviation a 2 digit number corresponding to their order
months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
          "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
#Give each 1 digit date and 0 before the date to maintain consistency
days = {"1": "01", "2": "02", "3": "03", "4": "04", "5": "05", "6": "06", "7": "07", "8": "08",
        "9": "09"}


def GetHours(gameIds):
    '''Takes the list argument of tuples [(id, game_id), ...]
       and returns a list of tuples [(id, hours), ...]'''
    global data, steamId, API_KEY
    #Update the steam id with the current one in the json file
    UpdateId()
    #Url to retrieve the game hours of the user's steam library
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steamId}&format=json'
    #Attempt a connection, return an error code if it fails
    try:
        response = requests.get(url)
    except:
        return 10
    #Check the response code and return and error code if it is the wrong code
    if response.status_code == 200:
        #Attempt to format the response into a dictionary, return an error code if it fails
        try:
            data = response.json()
        except:
            return 12
        #If the correct keys are in the dictionary
        if 'response' in data and 'games' in data['response']:
                finalList = []
                #Go through each game dictionary and go through each tuple in the given list,
                #and add the hours of the game with the corresponding id to the list if the game id in the tuple,
                #equals the game id in dictionary
                for game in data['response']['games']:
                    for entry in gameIds:
                        if game['appid'] == entry[1]:
                            finalList.append((entry[0], round((game['playtime_forever'] / 60), 1)))
                return finalList
    else:
        return 11


def GetGameDetails(appId, language='english'):
    '''Returns the release date in two forms and the developer of the given appid'''
    global data, steamId, API_KEY
    #Update the steam id with the id in the json file
    UpdateId()
    #Url for accessing the app's, corresponding to the given id, data
    url = f'https://store.steampowered.com/api/appdetails'
    #Parameters to add with the request. The appid, and language format
    params = {
        'appids': appId,
        'cc': 'us',  
        'l': language  
    }
    #Attempt to send the request through, return an error code if it fails
    try:
        response = requests.get(url, params=params)
    except:
        return 10
    #Attempt to convert the response to a dictionary formet, return an error code if it fails
    try:
        data = response.json()
    except:
        return 12
    #If the corrects keys are in the dictionary, access the release date and developers
    if str(appId) in data and data[str(appId)]['success']:
        details = data[str(appId)]['data']
        releaseDate = details.get('release_date', {}).get('date')
        developer = details.get('developers', [])
        #Attempt to convert the release date to a tuple with 2 date formats, return None if it fails
        try:
            ConvertDate(releaseDate)
        except:
            return None
        #Return the release date tuple and the first developer entry in a dictionary
        else:
            return {
                'release_date': ConvertDate(releaseDate),
                'developer': developer[0],
            }
    return None


def ConvertDate(date):
    '''Converts month day, year to a tuple containing (dd/mm/yyyy, yyyymmdd)'''
    #Remove the comma and split the argument into a list containing [month, day, year]
    date = date.replace(",", "")
    date = date.split()
    #Restructure the list to [day, month, year]
    date = [date[1], date[0], date[2]]
    #Convert the month to lowercase and replace it with the number version
    date[1] = months[(date[1].lower())]
    #If the date is a single digit, convert it to double digit e.g. 1 -> 01
    if date[0] in days:
        date[0] = days[date[0]]
    #Return a dictionary of the date in DD/MM/YYYY form and a pure integer form YYYYMMDD
    strDate = "/".join(date)
    intDate = int(date[2] + date[1] + date[0])
    return {"strdate": strDate, "intdate": intDate}


def GetBasicData():
    '''Gets the appid, name and hours of the user's steam library'''
    global data, steamId, API_KEY
    #Update the steam id with the id in the json file
    UpdateId()
    #Url for getting basic data about the user's owned games
    url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'

    params = {
        'key': API_KEY,
        'steamid': steamId,
        'format': 'json',
        'include_appinfo': True,  
        'include_played_free_games': True  
    }
    #Attempt to send the request to steam, return an error code if it fails
    try:
        response = requests.get(url, params=params)
    except:
        return 10
    #Attempt to convert the reponse to dictionary form, return an error code if it fails
    try:
        data = response.json()
    except:
        return 11
    #If the correct keys are in the dictionary
    if 'response' in data and 'games' in data['response']:
        games = data['response']['games']
        list = []
        #For each game in games, get the app id, name, and playtime
        for game in games:
            tup = {}
            appid = game.get('appid')
            name = game.get('name')
            playtimeForever = game.get('playtime_forever')
            #Convert the playtime to hour form and round to 1dcp
            playtimeForever = round((playtimeForever / 60), 1)
            #If the user has played more or equal to one hour of the game, add the game data to a list
            if playtimeForever >= 1:
                tup["appid"] = appid
                tup["name"] = name
                tup["playtime"] = playtimeForever
                list.append(tup)
        #Return the game list at the end
        return list
                
    else:
        return None


def CompileData():
    '''Accesses the GetBasicData and GetGameDetails functions and combines their data'''
    #Get basic data about the users library
    basicData = GetBasicData()
    #If the result is an integer, return the integer
    if isinstance(basicData, int):
        return basicData
    #If the result is something
    if basicData:
        
        blackList = []
        #For each game in the basic data list, add to the list the release date and the developer of the game
        for i in range(len(basicData)):
            moreDetails = GetGameDetails(basicData[i]["appid"])
            #If the extra details returns an integer, return the integer
            if isinstance(moreDetails, int):
                return moreDetails
            #If the more details is something, add the details to the game dictionary
            if moreDetails:
                basicData[i]["release_date"] = moreDetails["release_date"]
                basicData[i]["developer"] = moreDetails["developer"]
            #Add the current iteration in the loop to a blacklist if the more details is None
            else:
                blackList.append(i)
        final = []
        #Go through each game and add it to a new list if it isn't blacklisted
        for i in range(len(basicData)):
            if i in blackList:
                continue
            final.append(basicData[i])
        return final
    else:
        return None


def TestId(id):
    '''Tests if the argument is a valid steam id'''
    global steamId, data, API_KEY
    #Update the steam id with the id in the json file
    UpdateId()
    #Url for getting the user's owned games
    url = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={id}&format=json'
    #Attempt to get a request from steam, return an error code if it fails
    try:
        response = requests.get(url)
    except:
        return 10
    #Check the status code on the response, return an False if the status code is invalid
    if response.status_code == 200:
        #Return an error code if the response cannot be converted, return True if it doesn't fail
        try:
            jsonTest = response.json()
        except:
            return 12
        else:
            return True
    else:
        return False


def TestConnection():
    '''Checks if there is a proper connection to Steam'''
    global steamId, data, API_KEY
    #Update the steam id with the id in the json file
    UpdateId()
    #Url for getting the user's owned games
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steamId}&format=json"
    #Attempt to push the request to steam,
    #Return True if it succeeds, return False if it fails
    try:
        response = requests.get(url)
    except:
        return False
    else:
        return True


def UpdateId():
    '''Update the steam id with the id in the json file'''
    global steamId, data
    #Load the json data and update the accessible steam id with the one in the json file
    with open('data.json') as f:
        data = json.load(f)
    steamId = data["steam_id"]