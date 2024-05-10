import sqlite3
import steam_hours_update

DATABASE = "steam_db.db"

EXECUTE = ('''
SELECT name, hours, studios.studio_name
FROM my_steam_library
JOIN studios ON my_steam_library.studio_id = studios.id
ORDER BY hours DESC;''')


with sqlite3.connect(DATABASE) as f:
    cursor = f.cursor()
    cursor.execute(EXECUTE)
    results = cursor.fetchall()

print(f"{"name":<40}{"hours":<8}studio\n")
for tup in results:
    print(f"{tup[0]:<40}{tup[1]:<8}{tup[2]}")