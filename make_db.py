import steam_handle, sqlite3, os

os.chdir("C:/Users/ojkit/Documents/Steam DB")

dbname = "db_test.db"

def errorcheck(i):
    '''Checks the argument for the error code'''
    if i == 1:
        return False
    else:
        return True

def cleanse(list):
    '''Cleanses the names in the list of any strange characters like a trademark'''
    validchar = "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()`~[]}{|;\':\"\\,./<>? "
    for game in list:
        oldname = game['name']
        newname = ""
        for char in oldname:
            if char.lower() in validchar:
                newname += char
        game['name'] = newname
    return list

def makedb(makedb):
    '''Makes a databse, if it doesn't exist, of the user's steam library'''
    try:
        with open(makedb) as check:
            pass
    except:
        if not errorcheck(steam_handle.gethours([])):
            return 1
        with sqlite3.connect(makedb) as db:
            print("Creating database...")
            cursor = db.cursor()
            cursor.execute('CREATE TABLE IF NOT EXISTS studios (id INTEGER PRIMARY KEY, studio_name TEXT, studio_name_lower TEXT)')
            cursor.execute('''CREATE TABLE IF NOT EXISTS steam_library (
    id INTEGER PRIMARY KEY,
    name TEXT,
    studio_id INTEGER,
    hours REAL,
    steam_release_date TEXT,
    date_order INTEGER,
    game_id INTEGER,
    lower_name TEXT,
    FOREIGN KEY (studio_id) REFERENCES studios(id)
    )''')
            print("Compiling steam data...")
            gamedata = steam_handle.compiledata()
            gamedata = cleanse(gamedata)
            print("Sorting data...")
            for data in gamedata:
                cursor.execute('''INSERT INTO steam_library (name,  hours, steam_release_date, date_order, game_id, lower_name)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data["name"], data["playtime"], data["release_date"]["strdate"], data["release_date"]["intdate"], data["appid"], (data["name"]).lower()))
        
            studiolist = []
            for data in gamedata:
                if data['developer'] not in studiolist:
                    studiolist.append(data['developer'])
            for dev in studiolist:
                cursor.execute("INSERT INTO studios (studio_name, studio_name_lower) VALUES (?, ?)", (dev, dev.lower()))
            cursor.execute("SELECT id, studio_name FROM studios;")
            devs = cursor.fetchall()
            devsdict = {}
            for dev in devs:
                devsdict[dev[1]] = dev[0]
            for data in gamedata:
                cursor.execute(f"UPDATE steam_library SET studio_id = {devsdict[data["developer"]]} WHERE game_id = {data["appid"]}")
            print("Database finished.")

