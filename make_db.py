'''Function library for handling database table creation and deletion'''
import steam_handle, sqlite3, os

os.chdir("C:/Users/ojkit/Documents/Steam DB")


def Cleanse(list):
    '''Cleanses the names in the list of any strange characters like a trademark'''
    #String of accepted characters
    validchar = "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()`~[]}{|;\':\"\\,./<>? "
    #Go through each dictionary in the list and replace the name with the same name purged of all characters not in "validchar"
    for game in list:
        oldname = game['name']
        newname = ""
        for char in oldname:
            if char.lower() in validchar:
                newname += char
        game['name'] = newname
    return list

def MakeDb(database):
    '''Makes a databse, if it doesn't exist, of the user's steam library'''
    #Run the CompileData function from the steam_handle file and assign the result to a variable
    with sqlite3.connect(database) as db:
        print("Compiling steam library data...")
        gamedata = steam_handle.CompileData()
        #If the result is an integer, return the result
        if isinstance(gamedata, int):
            return gamedata
        print("Creating database...")
        #Delete the "steam_library" and "studios" table from the database
        DeleteTables(database)
        #In the database, execute the queries to create the studios table with the columns,
        #and create the steam_library database with the columns and a foreign key to studios
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
        
        
        #Cleanse all of the names in the results from unwanted characters like trademarks
        gamedata = Cleanse(gamedata)
        #Go through all of the game data and sort it into the steam_library table excluding the studio_id column
        print("Sorting data...")
        for data in gamedata:
            cursor.execute('''INSERT INTO steam_library (name,  hours, steam_release_date, date_order, game_id, lower_name)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (data["name"], data["playtime"], data["release_date"]["strdate"], data["release_date"]["intdate"], data["appid"], (data["name"]).lower()))
        #Add all of the unique developers in the game data to a list
        studiolist = []
        for data in gamedata:
            if data['developer'] not in studiolist:
                studiolist.append(data['developer'])
        #Add the each developer to the studios table
        for dev in studiolist:
            cursor.execute("INSERT INTO studios (studio_name, studio_name_lower) VALUES (?, ?)", (dev, dev.lower()))
        #Go through all of the developers in the studios table and put them in a dictionary,
        #with their value as their id in the studios table
        cursor.execute("SELECT id, studio_name FROM studios;")
        devs = cursor.fetchall()
        devsdict = {}
        for dev in devs:
            devsdict[dev[1]] = dev[0]
        #Go through each game and assign their studio_id column to the corresponding id,
        #of their developer, in the dictionary
        for data in gamedata:
            cursor.execute(f"UPDATE steam_library SET studio_id = {devsdict[data["developer"]]} WHERE game_id = {data["appid"]}")
        print("Database finished.")

def DeleteTables(database): 
    '''Delete the "steam_library" and "studios" table from the given database directory'''
    #Attempt to open the database, end the function otherwise
    try:
        with open(database) as f:
            pass
    except:
        return 0
    else:
        #Execute the queries in the database to remove the tables
        with sqlite3.connect(database) as db:
            cursor = db.cursor()
            db.execute("DROP TABLE steam_library;")
            db.execute("DROP TABLE studios;")
