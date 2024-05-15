import sqlite3
import steam_hours_update



DATABASE = "steam_db.db"
EXITNUM = 4
DATASPACING = {"name": 40, "hours": 8, "studios.studio_name": 25, "steam_release_date": 12}
DATAKEYPRINT = {1: "name", 2: "studios.studio_name", 3: "hours", 4: "steam_release_date"}
DATAKEYSORT = {1: "hours DESC", 2: "date_order DESC", 3: "lower_name ASC", 4: ""}
DATADISPLAY = {"name": "Name", "hours": "Hours", "studios.studio_name": "Studio", "steam_release_date": "Release date"}



def spacingcalc(string, key):
    if key not in DATASPACING:
        return False
    else:
        if DATASPACING[key] - len(string) < 0:
            return string
        final = ""
        final += string
        final += (" " * (DATASPACING[key] - len(string)))
        return final
        


def updatedatabasehours():
    execute = "SELECT id, game_id FROM steam_library;"
    results = exequery(execute)
    newresults = steam_hours_update.gethours(results)
    with sqlite3.connect("steam_db.db") as f:
        cursor = f.cursor()
        for tup in newresults:
            cursor.execute(f"UPDATE steam_library SET hours = {tup[1]} WHERE id = {tup[0]}")

            
def gettotalhours():
    '''Returns the total hours of the database entries through STEAM (not through the db file)'''
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, game_id FROM steam_library;")
        results = cursor.fetchall()
        results2 = steam_hours_update.gethours(results)
        total = 0
        for entry in results2:
            total += entry[1]
        return total

def exequery(execute):
    with sqlite3.connect(DATABASE) as f:
        cursor = f.cursor()
        cursor.execute(execute)
        results = cursor.fetchall()
        return results


def handleprint():
    print("\nWhat data to print?\n(Type the corresponding numbers seperated by a space)\n")
    print("1. Name\n2. Studio\n3. Hours\n4. Steam release date\n")
    userinp = input("> ")
    if not userinp:
        print("Invalid input, try again")
        return False
    else:
        userinp = userinp.split()
        try:
            for i in range(len(userinp)):
                userinp[i] = int(userinp[i])
                
        except:
            print("Invalid input, try again")
            return False
        try:
            for i in range(len(userinp)):
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
                sqlrun += f" ORDER BY {DATAKEYSORT[sort]};"
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
            
    

run = True
while run:
    print(f'''Make your choice:
1. Print data
2. Update database hours
3. Get total hours
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
            print("Updating...")
            updatedatabasehours()
        elif inp == 3:
            print("Fetching data...")
            total = gettotalhours()
            print(f"Total hours: {round(total, 1)} hours")
        elif inp == EXITNUM:
            run = False
            continue



