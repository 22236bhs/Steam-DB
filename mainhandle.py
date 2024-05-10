import sqlite3
import steam_hours_update



DATABASE = "steam_db.db"

EXECUTE = ('''
SELECT name, hours, studios.studio_name
FROM steam_library
JOIN studios ON steam_library.studio_id = studios.id
ORDER BY hours DESC;''')

def updatedatabasehours():
    with sqlite3.connect(DATABASE) as db:
        cursor = db.cursor()
        cursor.execute("SELECT id, game_id FROM steam_library;")
        results = cursor.fetchall()
        newresults = steam_hours_update.gethours(results)
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


with sqlite3.connect(DATABASE) as f:
    cursor = f.cursor()
    cursor.execute(EXECUTE)
    results = cursor.fetchall()

#updatedatabasehours()

print(f"{"name":<40}{"hours":<8}studio\n")
for tup in results:
    print(f"{tup[0]:<40}{tup[1]:<8}{tup[2]}")
