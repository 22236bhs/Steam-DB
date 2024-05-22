import sqlite3, json, os
import steam_handle

os.chdir("C:/Users/ojkit/Documents/Steam DB")

#Constants
DATABASE = "steam_db.db"
EXITNUM = 6
DATAKEYPRINT = {1: "name", 2: "studios.studio_name", 3: "hours", 4: "steam_release_date"}
DATAKEYSORT = {1: "hours DESC", 2: "date_order DESC", 3: "lower_name ASC", 4: ""}
DATADISPLAY = {"name": "Name", "hours": "Hours", "studios.studio_name": "Studio", "steam_release_date": "Release date"}

dataspacing = {"name": 0, "hours": 8, "studios.studio_name": 0, "steam_release_date": 14}

with open("data.json") as js:
    datajson = json.load(js)

def exequery(execute):
    '''Executes given query in the database'''
    with sqlite3.connect(DATABASE) as f:
        cursor = f.cursor()
        cursor.execute(execute)
        results = cursor.fetchall()
        return results


def errorcheck(i):
    if i == 1:
        return False
    else:
        return True


def errorhandle():
    print("Connection errors detected...")


def setupdataspacing():
    global dataspacing
    maxnamelength = 0
    maxstudiolength = 0
    try:
        results = exequery("SELECT name, studios.studio_name FROM steam_library JOIN studios ON steam_library.studio_id = studios.id;")
        
        for result in results:
            if (len(result[0])) > maxnamelength:
                maxnamelength = len(result[0])
            if len(result[1]) > maxstudiolength:
                maxstudiolength = len(result[1])
        maxnamelength += 5
        maxstudiolength += 5
    except:
        pass
    dataspacing["name"] = maxnamelength
    dataspacing["studios.studio_name"] = maxstudiolength

setupdataspacing()

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
    if not errorcheck(newresults):
        errorhandle()
        return 0
    with sqlite3.connect("steam_db.db") as f:
        cursor = f.cursor()
        for tup in newresults:
            cursor.execute(f"UPDATE steam_library SET hours = {tup[1]} WHERE id = {tup[0]}")


def searchdata():
    selectuserinp = True
    while selectuserinp:
        print('''\nChoose what to search by
    1. Name
    2. Studio
    3. Greater than X hours
    4. Less than X hours
    5. Before release date
    6. After release date''')
        userinp = input("> ")
        try:
            userinp = int(userinp)
        except:
            print("Invalid input")
        else:
            date = False
            integer = False
            if userinp == 1:
                search = f"WHERE steam_library.lower_name LIKE \"%"
                join = "%\""
                order = " ORDER BY steam_library.lower_name ASC;"
            elif userinp == 2:
                search = f"WHERE studios.studio_name LIKE \"%"
                join = "%\""
                order = " ORDER BY studios.studio_name ASC;"
            elif userinp == 3:
                search = "WHERE steam_library.hours >= "
                join = ""
                order = " ORDER BY steam_library.hours DESC;"
                integer = True
            elif userinp == 4:
                search = "WHERE steam_library.hours <= "
                join = ""
                order = " ORDER BY steam_library.hours DESC;"
                integer = True
            elif userinp == 5:
                search = "WHERE steam_library.date_order <= "
                join = ""
                order = " ORDER BY steam_library.date_order DESC;"
                date = True
            elif userinp == 6:
                search = "WHERE steam_library.date_order >= "
                join = ""
                order = " ORDER BY steam_library.date_order DESC"
                date = True

            else:
                print("Invalid option")
                return 0
            

            setuptosearch = True
            while setuptosearch:
                print("\nType what to search")
                if not date and not integer:
                    tosearch = input("> ")
                elif date:
                    tosearch = input("Enter the date in the format (DD/MM/YYYY)\nEnter \"back\" to go back\n> ").lower()
                    try:
                        if tosearch == "back":
                            setuptosearch = False
                            continue
                        tosearch = convertdate(tosearch)
                        if len(tosearch) != 8:
                            print("Invalid date")
                            continue
                    except:
                        print("Invalid date")
                        continue
                elif integer:
                    tosearch = input("Enter \"back\" to go back\n> ").lower()
                    try:
                        if tosearch == "back":
                            setuptosearch = False
                            continue
                        tosearch = int(tosearch)
                        tosearch = str(tosearch)
                    except:
                        print("Invalid input")
                        continue
                
                search += tosearch
                search += join
                results = exequery(f'''SELECT steam_library.name, steam_library.hours, studios.studio_name, steam_library.steam_release_date
    FROM steam_library
    JOIN studios ON studios.id = steam_library.studio_id                       
    {search}
    {order}''')
                print("Results:\n")
                print(f"{spacingcalc("Name", "name")}{spacingcalc("Hours", "hours")}", end='')
                print(f"{spacingcalc("Studio", "studios.studio_name")}{spacingcalc("Release date", "steam_release_date")}\n")
                for result in results:
                    print(f"{spacingcalc(result[0], "name")}{spacingcalc(str(result[1]), "hours")}", end='')
                    print(f"{spacingcalc(result[2], "studios.studio_name")}{spacingcalc(result[3], "steam_release_date")}")
                setuptosearch = False
                selectuserinp = False
            

            
def gettotalhours():
    '''Returns the total hours of the database entries through STEAM (not through the db file)'''
    results = exequery("SELECT id, game_id FROM steam_library;")
    results2 = steam_handle.gethours(results)
    if not errorcheck(results2):
        errorhandle()
        return 0
    total = 0
    for entry in results2:
        total += entry[1]
    print(f"Total hours: {round(total, 1)} hours")
    


def settings():
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
                if not errorcheck(idtest):
                    errorhandle()
                    return 0
                if idtest:
                    print("Steam id updated")
                    datajson["steam_id"] = str(steamid)
                    with open("data.json", 'w') as js:
                        json.dump(datajson, js)
                    return 0

                else:
                    print("Invalid Steam id")
                    return 0

                
        elif userinp == 2:
            print('''\nAre you sure you want to redo the database?
The old database with be DELETED and replaced with a new one.
Note: (Only games with more than 1 hour played will be added to the new database)\n''')
            proceed = input("Proceed? (Y/N)\n> ").lower()
            if proceed == "n":
                return 0
            elif proceed == "y":
                try:
                    os.remove("db_test.db")
                except:
                    pass
                check = steam_handle.make_db.makedb("db_test.db")
                if not errorcheck(check):
                    errorhandle()
                    return 0
                setupdataspacing()
            else:
                print("Invalid input")



                        

        elif userinp == BACKNUM:
            return 0
        else:
            print("Invalid option")
            return 0



def handleprint():
    '''Handles printing out data based on user inputs'''
    print("\nWhat data to print?\n(Type the corresponding numbers seperated by a space)\n")
    print("1. Name\n2. Studio\n3. Hours\n4. Steam release date\n5. All\n")
    userinp = input("> ")
    if not userinp:
        print("Invalid input, try again")
        return False
    else:
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
            return False
        try:
            for i in range(len(userinp)):
                if userinp[i] == 5:
                    userinp = ['name', 'studios.studio_name', 'hours', 'steam_release_date']
                    break
                userinp[i] = DATAKEYPRINT[userinp[i]]
        except:
            print("Invalid number, try again")
            return False
        
        selectstr = ", ".join(userinp)
        sqlrun = "SELECT "
        sqlrun += selectstr
        sqlrun += " FROM steam_library"
        print("What will the data be ordered by?\n")
        print("1. Hours\n2. Release date\n3. Alphabetical\n4. Default")
        sort = input("> ")
        try:
            sort = int(sort)
        except:
            print("Invalid input, try again")
            return False
        if sort not in DATAKEYSORT:
            print("Invalid number, try again")
            return False
        else:  
            sqlrun += " JOIN studios ON steam_library.studio_id = studios.id"
            if DATAKEYSORT[sort]:
                sqlrun += f" ORDER BY {DATAKEYSORT[sort]}"
            sqlrun += ";"
            results = exequery(sqlrun)
            tup = results[0]
            size = len(tup)
            finalprint = ""
            for i in range(size):
                finalprint += spacingcalc(DATADISPLAY[userinp[i]], userinp[i])
            print(f"{finalprint}\n")
            for a in range((len(results))):
                finalprint = ""
                for i in range(size):
                    finalprint += spacingcalc(str(results[a][i]), userinp[i])
                print(finalprint)
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
                with open("data.json") as test:
                    pass
            except:
                test = open("data.json", "w")
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
                    if not errorcheck(idtest):
                        errorhandle()
                        quit()
                    if not idtest:
                        print("Invalid Steam id")
                        continue
                    break
                newapikey = input("Enter your api_key (Type 'quit' to quit)").lower()
                

                        




            
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



