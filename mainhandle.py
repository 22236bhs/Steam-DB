'''File for input/output operations'''
import sqlite3, json, os
import steam_handle, make_db

os.chdir("C:/Users/ojkit/Documents/Steam DB")

#Constants
DATABASE = "db_test.db"
TESTDB = "db_test.db"
JSONFILE = "data.json"
EXITNUM = 6
DATAKEYPRINT = {1: "name", 2: "studios.studio_name", 3: "hours", 4: "steam_release_date"}
DATAKEYSORT = {1: "hours DESC", 2: "date_order DESC", 3: "lower_name ASC", 4: ""}
DATADISPLAY = {"name": "Name", "hours": "Hours", "studios.studio_name": "Studio", "steam_release_date": "Release date"}

dataspacing = {"name": 0, "hours": 0, "studios.studio_name": 0, "steam_release_date": 17}

with open(JSONFILE) as js:
    datajson = json.load(js)

def exequery(execute):
    '''Executes given query in the database'''
    with sqlite3.connect(DATABASE) as f:
        cursor = f.cursor()
        cursor.execute(execute)
        results = cursor.fetchall()
        return results


def errorcheck(i, prnt):
    '''Checks the argument for the error code'''
    errordict = {10: {"code": "No internet connection detected"},
                 11: {"code": "Error regarding WiFi network"},
                 12: {"code": "Error regarding network response"}}
    if isinstance(i, int):
        if i in errordict:
            if prnt:
                print(errordict[i]["code"])
            return True
        else:
            return False
    else:
        return False







def setupdataspacing():
    '''Setup the spacing of printing of the studio name and game name'''
    global dataspacing
    maxnamelength = 0
    maxstudiolength = 0
    maxhourlength = 0
    try:
        with open(DATABASE) as test:
            pass
        results = exequery("SELECT name, studios.studio_name, hours FROM steam_library JOIN studios ON steam_library.studio_id = studios.id;")
        for result in results:
            if len(result[0]) > maxnamelength:
                maxnamelength = len(result[0])
            if len(result[1]) > maxstudiolength:
                maxstudiolength = len(result[1])
            if len(str(result[2])) > maxhourlength:
                maxhourlength = len(str(result[2]))
        if len("Name") > maxnamelength:
            maxnamelength = len("Name")
        if len("Hours") > maxhourlength:
            maxhourlength = len("Hours")
        if len("Studio") > maxstudiolength:
            maxstudiolength = len("Studio")
        maxnamelength += 5
        maxstudiolength += 5
        maxhourlength += 5
    except:
        pass
    dataspacing["name"] = maxnamelength
    dataspacing["studios.studio_name"] = maxstudiolength
    dataspacing["hours"] = maxhourlength



def convertdate(date):
    '''Recieves the arguments DD/MM/YYYY and returns YYYYMMDD'''
    date = date.split("/")
    date = date[2] + date[1] + date[0]
    return date


def spacingcalc(string, key):
    '''Uses the given key to determine how much space should be left after the string and returns it'''
    if key not in dataspacing:
        return False
    else:
        if dataspacing[key] - len(string) < 0:
            return string
        else:
            final = ""
            final += string
            final += (" " * (dataspacing[key] - len(string)))
            return final
        


def updatedatabasehours():
    '''Updates the database with the user's current Steam hours'''
    execute = "SELECT id, game_id FROM steam_library;"
    results = exequery(execute)
    newresults = steam_handle.gethours(results)
    if errorcheck(newresults, True):
        return 0
    with sqlite3.connect("steam_db.db") as f:
        cursor = f.cursor()
        for tup in newresults:
            cursor.execute(f"UPDATE steam_library SET hours = {tup[1]} WHERE id = {tup[0]}")
        setupdataspacing()


def searchdata():
    '''Searches the database for custom matches'''
    keydict = {1: {"search": "WHERE steam_library.lower_name LIKE \"%",
                    "join": "%\"",
                    "order": " ORDER BY steam_library.lower_name ASC;",
                    "date": False,
                    "integer": False}, 
               2: {"search": "WHERE studios.studio_name LIKE \"%",
                   "join": "%\"",
                   "order": " ORDER BY studios.studio_name_lower ASC;",
                   "date": False,
                   "integer": False},
                3: {"search": "WHERE steam_library.hours >= ",
                    "join": "",
                    "order": " ORDER BY steam_library.hours DESC;",
                    "date": False,
                    "integer": True},
                4: {"search": "WHERE steam_library.hours <= ",
                    "join": "",
                    "order": " ORDER BY steam_library.hours DESC;",
                    "date": False,
                    "integer": True},
                5: {"search": "WHERE steam_library.date_order <= ",
                    "join": "",
                    "order": " ORDER BY steam_library.date_order DESC;",
                    "date": True,
                    "integer": False},
                6: {"search": "WHERE steam_library.date_order >= ",
                    "join": "",
                    "order": " ORDER BY steam_library.date_order DESC;",
                    "date": True,
                    "integer": False}}
    selectuserinp = True
    while selectuserinp:
        print('''\nChoose what to search by
    1. Name
    2. Studio
    3. Greater than X hours
    4. Less than X hours
    5. Before release date
    6. After release date
    7. Back''')
        userinp = input("> ")
        try:
            userinp = int(userinp)
        except:
            print("Invalid input")
        else:
            
            if userinp == 7:
                break
            elif userinp in keydict:
                order = keydict[userinp]["order"]
                search = keydict[userinp]["search"]
                join = keydict[userinp]["join"]
                date = keydict[userinp]["date"]
                integer = keydict[userinp]["integer"]      
            

            setuptosearch = True
            while setuptosearch:
                print("\nEnter what to search")
                
                if date:
                    print("Enter the date in the format (DD/MM/YYYY) ")
                print("Type |back| to go back")
                tosearch = input("> ")
                if tosearch == "|back|":
                    setuptosearch = False
                    continue
                
                elif integer:
                    if isint(tosearch):
                        pass
                    else:
                     
                        print("Invalid input, must be integer")
                        continue

                elif date:
                    try:
                        tosearch = convertdate(tosearch)
                    except:
                        print("Invalid input")
                        continue
                    if len(tosearch) != 8:
                        print("Invalid date")
                        continue

                search += tosearch
                search += join
                results = exequery(f'''SELECT steam_library.name, steam_library.hours, studios.studio_name, steam_library.steam_release_date
    FROM steam_library
    JOIN studios ON studios.id = steam_library.studio_id                       
    {search}
    {order}''')
                finalprint = (" " * 5)
                finalprint += (spacingcalc("Name", "name"))
                finalprint += (spacingcalc("Hours", "hours"))
                finalprint += (spacingcalc("Studio", "studios.studio_name"))
                finalprint += (spacingcalc("Release date", "steam_release_date"))
                finalprint += "\n"
                print("Results:\n")
                print(finalprint)
                finalprint = (" " * 5)
                
                for result in results:
                    finalprint = (" " * 5)
                    finalprint += (spacingcalc(result[0], "name"))
                    finalprint += (spacingcalc(str(result[1]), "hours"))
                    finalprint += (spacingcalc(result[2], "studios.studio_name"))
                    finalprint += (spacingcalc(result[3], "steam_release_date"))
                    print("-" * (len(finalprint)))
                    print(finalprint)
                if len(finalprint) != 5:
                    print("-" * (len(finalprint)))
                setuptosearch = False
                selectuserinp = False
            

            
def gettotalhours():
    '''Returns the total hours of the database entries through STEAM (not through the db file)'''
    results = exequery("SELECT id, game_id FROM steam_library;")
    results2 = steam_handle.gethours(results)
    if errorcheck(results2, True):
        return 0
    total = 0
    for entry in results2:
        total += entry[1]
    print(f"Total hours: {round(total, 1)} hours")


def isint(i):
    '''Returns True if the argument can be an integer, else return False'''
    try:
        i = int(i)
    except:
        return False
    else:
        return True
    


def settings():
    '''Settings section of the interface'''
    global datajson
    BACKNUM = 3
    print(f'''\n1. Change steam id
2. Remake steam database
{BACKNUM}. Back''')
    userinp = input("> ")
    try:
        userinp = int(userinp)
    except:
        print("Invalid input")
        return 0
    else:
        if userinp == 1:
            print("\nEnter your steam id")
            steamid = input("> ")
            try:
                steamid = int(steamid)
            except:
                print("Invalid input")
                return 0
            else:
                idtest = steam_handle.testid(str(steamid))
                if errorcheck(idtest, True):
                    return 0
                if idtest:
                    print("Steam id updated")
                    datajson["steam_id"] = str(steamid)
                    with open(JSONFILE, 'w') as js:
                        json.dump(datajson, js)
                    return 0

                else:
                    print("Invalid Steam id")
                    return 0

                
        elif userinp == 2:
            print('''\nAre you sure you want to redo the database?
THe old data will be DELETED and replaced with new data.
Note: (Only games with more than 1 hour played will be added to the new database)\n''')
            proceed = input("Proceed? (Y/N)\n> ").lower()
            if proceed == "n":
                return 0
            elif proceed == "y":
                if steam_handle.testconnection():
                    make_db.deletetables(TESTDB)
                    with sqlite3.connect(TESTDB) as test:
                        pass
                    check = make_db.makedb(TESTDB)
                    if errorcheck(check, True):
                        return 0
                    setupdataspacing()
                else:
                    print("Connection errors")

            else:
                print("Invalid input")



                        

        elif userinp == BACKNUM:
            return 0
        else:
            print("Invalid option")
            return 0



def handleprint():
    '''Handles printing out data based on user inputs'''
    global dataspacing
    getwhatdata = True
    while getwhatdata:
        print("\nWhat data to print?\n(Type the corresponding numbers seperated by a space)\n")
        print("1. Name\n2. Studio\n3. Hours\n4. Steam release date\n5. All\n6. Back\n")
        userinp = input("> ")
        if not userinp:
            print("Invalid input, try again")
            continue
        else:
            if userinp == "6":
                return 0
            userinp = userinp.split()
            try:
                final = []
                for i in range(len(userinp)):
                    userinp[i] = int(userinp[i])
                    if userinp[i] not in final:
                        final.append(userinp[i])
                userinp = final
                    
            except:
                print("Invalid input, try again")
                continue
            try:
                for i in range(len(userinp)):
                    if userinp[i] == 5:
                        userinp = ['name', 'studios.studio_name', 'hours', 'steam_release_date']
                        break
                    userinp[i] = DATAKEYPRINT[userinp[i]]
            except:
                print("Invalid number, try again")
                continue
            
            selectstr = ", ".join(userinp)
            sqlrun = "SELECT "
            sqlrun += selectstr
            sqlrun += " FROM steam_library"
            getdataorder = True
            while getdataorder:
                print("What will the data be ordered by?\n")
                print("1. Hours\n2. Release date\n3. Alphabetical\n4. Default\n5. Back\n")
                sort = input("> ")
                if sort == "5":
                    getdataorder = False
                    continue
                if isint(sort):
                    sort = int(sort)
                else:
                    print("Invalid input, try again")
                    continue
                if sort not in DATAKEYSORT:
                    print("Invalid number, try again")
                    continue
                else:  
                    sqlrun += " JOIN studios ON steam_library.studio_id = studios.id"
                    if DATAKEYSORT[sort]:
                        sqlrun += f" ORDER BY {DATAKEYSORT[sort]}"
                    sqlrun += ";"
                    results = exequery(sqlrun)
                    tup = results[0]
                    size = len(tup)
                    finalprint = (" " * 5)
                    for i in range(size):
                        finalprint += spacingcalc(DATADISPLAY[userinp[i]], userinp[i])
                    print(f"{finalprint}\n")
                    for a in range((len(results))):
                        finalprint = (" " * 5)
                        for i in range(size):
                            finalprint += spacingcalc(str(results[a][i]), userinp[i])
                        print("-" * (len(finalprint)))    
                        print(finalprint)
                        getdataorder = False
                        getwhatdata = False
                    if len(finalprint) != 5:
                        print("-" * (len(finalprint)))
                        


def filechecks(): 
    dbcheck = True    
    while dbcheck:
        try:
            with open(DATABASE) as test:
                pass
        except:
            print("No database found.\nCreate a database?\n(Y/N)\n")
            proceed = input("> ").lower()
            if proceed == "y":
                pass
            elif proceed == "n":
                quit()
            else:
                print("Invalid input")
                continue
            try:
                with open(JSONFILE) as test:
                    pass
            except:
                test = open(JSONFILE, "w")
                json.dump({"steam_id": "", "api_key": ""}, test)
                test.close()
                while True:
                    newsteamid = input("Enter your steam id (Type 'quit' to quit)").lower()
                    if newsteamid == "quit":
                        quit()
                    try:
                        newsteamid = int(newsteamid)
                        newsteamid = str(newsteamid)
                    except:
                        print("Invalid input")
                        continue
                    idtest = steam_handle.testid(newsteamid)
                    if errorcheck(idtest, True):
                        quit()
                    if not idtest:
                        print("Invalid Steam id")
                        continue
                    break
                newapikey = input("Enter your api_key (Type 'quit' to quit)").lower()
        else:
            with open(JSONFILE) as test:
                dbcheck = False
                continue
                


setupdataspacing()

            
run = True
while run:
    print(f'''\nMake your choice:
1. Print data
2. Search data
3. Update database hours
4. Get total hours
5. Settings
{EXITNUM}. Exit''')
    try:
        inp = int(input("> "))
    except:
        print("Invalid input")
    else:
        if inp == 1:
            handleprint()
            print()
        elif inp == 2:
            searchdata()
        elif inp == 3:
            print("Updating...")
            updatedatabasehours()
        elif inp == 4:
            print("Fetching data...")
            gettotalhours()
        elif inp == 5:
            settings()
        elif inp == EXITNUM:
            run = False
            continue
        else:
            print("Invalid choice")

