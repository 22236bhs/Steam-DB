import sqlite3
import steam_hours_update



DATABASE = "steam_db.db"
EXITNUM = 4

EXECUTE = ('''
SELECT name, hours, studios.studio_name
FROM steam_library
JOIN studios ON steam_library.studio_id = studios.id
ORDER BY hours DESC;''')

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
    
results = exequery(EXECUTE)


run = True
while run:
    print(f'''Make your choice:
1. Print name, hours, and studio sorted by hours
2. Update database hours
3. Get total hours
{EXITNUM}. Exit''')
    try:
        inp = int(input("> "))
    except:
        print("Invalid input")
    else:
        if inp == 1:
            print(f"{"name":<40}{"hours":<8}studio\n")
            for tup in results:
                print(f"{tup[0]:<40}{tup[1]:<8}{tup[2]}")
        elif inp == 2:
            print("Updating...")
            updatedatabasehours()
            results = exequery(EXECUTE)
        elif inp == 3:
            total = gettotalhours()
            print(f"Total hours: {round(total, 1)} hours")
        elif inp == EXITNUM:
            run = False
            continue



