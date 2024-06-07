'''File for input/output operations'''
import sqlite3, json, os

import steam_handle, make_db, error_handle

os.chdir("C:/Users/ojkit/Documents/Steam DB") #Directory

#Constants
DATABASE = "steam_db.db"
JSONFILE = "data.json"
DATAKEYPRINT = {1: "name", 2: "studios.studio_name", 3: "hours", 4: "steam_release_date"} #Convert user input as number to print option
DATAKEYSORT = {1: "hours DESC", 2: "date_order DESC", 3: "lower_name ASC", 4: ""} #Convert user input as number to sort option
DATADISPLAY = {"name": "Name", "hours": "Hours", "studios.studio_name": "Studio", "steam_release_date": "Release date"} #Convert the key to a string suitable for display

dataspacing = {"name": 0, "hours": 0, "studios.studio_name": 0, "steam_release_date": 17} #The allowed spacing when printing corresponding data

with open(JSONFILE) as js: #Get json file data
    datajson = json.load(js)

def PrintOutData(data, format):
    '''Prints out each tuple in data according to the format. The size of the tuples and the format must be the same'''
    TotalSpace = 5
    sep = TotalSpace
    for i in range(len(format)): #Get the maximum length of what can be printed out. used for the seperating line
        TotalSpace += dataspacing[format[i]] 
    FinalPrint = " " * sep #Start the header printing with "sep" spaces
    for i in range(len(format)): #Add each header in suitable display formet and add the correct amount of spaces afterwards
        FinalPrint += SpacingCalc(DATADISPLAY[format[i]], format[i])
    print(FinalPrint)
    
    print("-" * TotalSpace) #Add a line to seperate data
    if len(data) > 0: #If there is data to print
        for a in range(len(data)): #For each tuple in the data list as "a"
            FinalPrint = " " * sep #Start the line with "sep" amount of spaces
            for i in range(len(data[a])): #For each entry in the selected tuple
                FinalPrint += SpacingCalc(str(data[a][i]), format[i]) #Add the entry to FinalPrint with the correct amount of spaces
            print(FinalPrint) #Print the finished line
            print("-" * TotalSpace) #Add a line to seperate data



def ExeQuery(execute):
    '''Executes given query in the database'''
    with sqlite3.connect(DATABASE) as f:
        cursor = f.cursor()
        cursor.execute(execute)
        results = cursor.fetchall()
        return results





def SetupDataSpacing():
    '''Setup the spacing of printing of the studio name and game name'''
    global dataspacing #Access the dataspacing dictionary
    maxnamelength = 0   #Variables for the max length of each value type
    maxstudiolength = 0
    maxhourlength = 0
    try:
        with open(DATABASE) as test:
            pass
        #Access the all of the data that can be printed out excluding release date
        results = ExeQuery("SELECT name, studios.studio_name, hours FROM steam_library JOIN studios ON steam_library.studio_id = studios.id;") 
        for result in results: #Go through all of the data and assign the variables with the longest length of the corresponding data
            if len(result[0]) > maxnamelength:
                maxnamelength = len(result[0])
            if len(result[1]) > maxstudiolength:
                maxstudiolength = len(result[1])
            if len(str(result[2])) > maxhourlength:
                maxhourlength = len(str(result[2]))
        #If a length isn't longer than it's corresponding header, set the header length as the largest length
        if len("Name") > maxnamelength:
            maxnamelength = len("Name")
        if len("Hours") > maxhourlength:
            maxhourlength = len("Hours")
        if len("Studio") > maxstudiolength:
            maxstudiolength = len("Studio")
        
    except:
        pass
    #Add 5 to each to add some space between the longest value of it's category and the next value
    maxnamelength += 5
    maxstudiolength += 5
    maxhourlength += 5
    #Add the lengths to a dictionary
    dataspacing["name"] = maxnamelength
    dataspacing["studios.studio_name"] = maxstudiolength
    dataspacing["hours"] = maxhourlength



def ConvertDate(date):
    '''Recieves the arguments DD/MM/YYYY and returns YYYYMMDD'''
    date = date.split("/")
    date = date[2] + date[1] + date[0]
    return date


def SpacingCalc(string, key):
    '''Uses the given key to determine how much space should be left after the string and returns it'''
    if key not in dataspacing:
        return False
    else:
        #Make a variable and add the string plus the amount of remaining space allowed
        final = ""
        final += string
        final += (" " * (dataspacing[key] - len(string)))
        return final
        


def UpdateDatabaseHours():
    '''Updates the database with the user's current Steam hours'''
    execute = "SELECT id, game_id FROM steam_library;"
    results = ExeQuery(execute)
    #Replace the game id in each tuple with the corresponding hours the user has
    newresults = steam_handle.GetHours(results)
    #if the function returned an error, return nothing
    if error_handle.ErrorCheck(newresults):
        return 0
    #Go through each tuple in the results and update the database with those new hours
    for tup in newresults:
        ExeQuery(f"UPDATE steam_library SET hours = {tup[1]} WHERE id = {tup[0]}")
    #Remake the dataspacing dictionary
    SetupDataSpacing()


def SearchData():
    '''Searches the database for custom matches'''
    #Dictionary to assign variables depending on the chosen option
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
    while selectuserinp: #Search by loop
        print('''\nChoose what to search by
    1. Name
    2. Studio
    3. Greater than X hours
    4. Less than X hours
    5. Before release date
    6. After release date
    7. Back''')
        userinp = input("> ")
        try: #Check if the input is an integer
            userinp = int(userinp)
        except:
            print("Invalid input")
        else:
            #Check if the user input is the go back option
            if userinp == 7:
                break
            #If the user input is a valid option, assign the variables to the chosen option
            elif userinp in keydict:
                order = keydict[userinp]["order"]
                search = keydict[userinp]["search"]
                join = keydict[userinp]["join"]
                date = keydict[userinp]["date"]
                integer = keydict[userinp]["integer"]  
            #If the user input is out of range, restart the search by loop    
            else:
                print("Invalid option")
                continue

            setuptosearch = True
            while setuptosearch: #Search loop
                print("\nEnter what to search")
                
                if date: #If the user is searching for date, print out the additional info
                    print("Enter the date in the format (DD/MM/YYYY) ")
                print("Type \"/back\" to go back")
                tosearch = input("> ")
                #break out of the search loop and go back to the search by loop if the user types "/back"
                if tosearch == "/back":
                    setuptosearch = False
                    continue
                #Reprompt the user if they are searching by number and don't input a number
                elif integer:
                    try:
                        tosearch = float(tosearch)
                        tosearch = str(tosearch)
                    except:
                        print("Invalid input, must be number")
                        continue
                    
                #Attempt to convert the user input to a date format fit for searching
                elif date:
                    try:
                        tosearch = ConvertDate(tosearch)
                    except:
                        print("Invalid input")
                        continue
                    if len(tosearch) != 8:
                        print("Invalid date")
                        continue
                #Add the previous variables together in one query and execute it in the database
                search += tosearch
                search += join
                results = ExeQuery(f'''SELECT steam_library.name, studios.studio_name, steam_library.hours, steam_library.steam_release_date
    FROM steam_library
    JOIN studios ON studios.id = steam_library.studio_id                       
    {search}
    {order}''')
                
                print("Results:\n")
                #Run the PrintOutData function to format all of the data and print it
                PrintOutData(results, ["name", "studios.studio_name", "hours", "steam_release_date"])
                #End both of the loops
                setuptosearch = False
                selectuserinp = False
            

            
def GetTotalHours():
    '''Prints the total hours of the database entries through the database (not through steam)'''
    results = ExeQuery("SELECT hours FROM steam_library;")
    total = 0
    #Go through each game and add up the hours in the database
    for num in results:
        total += num[0]
    print(f"Total hours: {round(total, 1)} hours")
    #Get the amount of entries in the database and divide the total hours,
    #by the game count to get the average hours per game
    gamecount = len(results)
    average = total / gamecount
    print(f"Average hours: {round(average, 1)} hours")


def IsInt(i):
    '''Returns True if the argument can be an integer, else return False'''
    try:
        i = int(i)
    except:
        return False
    else:
        return True
    


def Settings():
    '''Settings section of the interface'''
    global datajson
    BACKNUM = 3
    MainSelect = True
    while MainSelect: #Main selection loop
        print(f'''\n1. Change steam id
2. Remake steam database
{BACKNUM}. Back''')
        userinp = input("> ")
        #Check if the user input is an integer
        try:
            userinp = int(userinp)
        except:
            print("Invalid input")
            continue
        else:
            if userinp == 1:
                GetId = True
                while GetId: #get id loop
                    print("\nEnter your steam id\nType \"/back\" to go back")
                    steamid = input("> ")
                    #Break out of the get id loop and back to the main selection loop if the user types "/back"
                    if steamid == "/back":
                        GetId = False
                        continue
                    #Attempt to convert the input to integer, reprompt the user if it fails
                    try:
                        steamid = int(steamid)
                    except:
                        print("Invalid input")
                        continue
                    else:
                        #Test if the id is a valid steam id, reprompt the user if it isn't or an internet error occurs 
                        idtest = steam_handle.TestId(str(steamid))
                        
                        if not idtest:
                            print("Invalid Steam id")
                            continue
                        if error_handle.ErrorCheck(idtest):
                            continue
                        #Update the json file with the new steam id and go back to the main selection loops
                        if idtest:
                            print("Steam id updated")
                            datajson["steam_id"] = str(steamid)
                            with open(JSONFILE, 'w') as js:
                                json.dump(datajson, js)
                            GetId = False
                            continue
                        
                    
            elif userinp == 2:
                RedoDatabase = True
                while RedoDatabase: #Database creation loop
                    print('''\nAre you sure you want to redo the database?
The old data will be DELETED and replaced with new data.
Note: (Some games that are unfit for formatting in the database,
as well as games with under 1 hour, won't be added to the database)
                          
Note 2: (The steam account being accessed must have the library data
set to public in order for the generation to work)\n''')
                    proceed = input("Proceed? (Y/N)\n> ").lower()
                    #Break out of the database creation loop and return to the main selection loop if the user types "n"
                    if proceed == "n":
                        RedoDatabase = False
                        continue
                    elif proceed == "y":
                        #Test the internet connection, reprompt the user if an error occurs
                        if steam_handle.TestConnection():
                            #Create the database if it for some reason, doesn't exist
                            with sqlite3.connect(DATABASE) as test:
                                pass
                            #Create the database and assign the potential function return to a variable
                            check = make_db.MakeDb(DATABASE)
                            #If the function return is an error code, break out of the database creation loop and return to the main selection loop
                            if error_handle.ErrorCheck(check):
                                RedoDatabase = False
                                continue
                            #Redo the data spacing dictionary after the new database is compiled and return to the main selection loop
                            SetupDataSpacing()
                            RedoDatabase = False
                            continue
                        else:
                            print("Connection errors")
                    #Reprompt the user if the input is not "y" or "n"
                    else:
                        print("Invalid input")
            #If the user option is to go back, end the function
            elif userinp == BACKNUM:
                return 0
            #If the user option is out of range, reprompt the user
            else:
                print("Invalid option")
                continue



def HandlePrint():
    '''Handles printing out data based on user inputs'''
    global dataspacing
    getwhatdata = True
    while getwhatdata: #Data choice loop
        print("\nWhat data to print?\n(Type the corresponding numbers seperated by a space)\n")
        print("1. Name\n2. Studio\n3. Hours\n4. Steam release date\n5. All\n6. Back\n")
        userinp = input("> ")
        #If the user didn't input anything, reprompt the user
        if not userinp:
            print("Invalid input, try again")
            continue
        #If the user entered the go back number, end the function
        else:
            if userinp == "6":
                return 0
            #Split the user input into a list and attempt to make each entry an integer,
            #Otherwise reprompt the user. Also reprompt the user if the list has no entries
            userinp = userinp.split()
            if len(userinp) == 0:
                print("Invalid input, try again")
                continue
            try:
                #Add each unique entry to "final" and reassign "userinp" with "final"
                final = []
                for i in range(len(userinp)):
                    userinp[i] = int(userinp[i])
                    if userinp[i] not in final:
                        final.append(userinp[i])
                userinp = final
            #If one of the entries isn't an integer, reprompt the user
            except:
                print("Invalid input, try again")
                continue
            #Attempt to convert each number in the input list to a corresponding choice in the DATAKEYPRINT dictionary
            #If 5 is detected in the list, the "all" option, preset the list and break out of the loop
            #If the conversion fails, repromt the user
            try:
                for i in range(len(userinp)):
                    if userinp[i] == 5:
                        userinp = ['name', 'studios.studio_name', 'hours', 'steam_release_date']
                        break
                    userinp[i] = DATAKEYPRINT[userinp[i]]
            except:
                print("Invalid number, try again")
                continue
            #Combine each entry in the user input list into a string seperated by commas
            selectstr = ", ".join(userinp)
            #Create the selecting part of the qury
            sqlrun = "SELECT "
            sqlrun += selectstr
            sqlrun += " FROM steam_library"
            getdataorder = True
            while getdataorder: #Get order loop
                print("What will the data be ordered by?\n")
                print("1. Hours\n2. Release date\n3. Alphabetical\n4. Default\n5. Back\n")
                sort = input("> ")
                #Go back to the data choice loop if the user enters 5
                if sort == "5":
                    getdataorder = False
                    continue
                #Attempt to convert the input to an integer, reprompt the user if it fails
                if IsInt(sort):
                    sort = int(sort)
                else:
                    print("Invalid input, try again")
                    continue
                #If the input is out of range, reprompt the user
                if sort not in DATAKEYSORT:
                    print("Invalid number, try again")
                    continue
                else:  
                    #Add finish the query by adding the join section and ending with the sorting part, 
                    #if the sort option has a value in the dictionary
                    sqlrun += " JOIN studios ON steam_library.studio_id = studios.id"
                    if DATAKEYSORT[sort]:
                        sqlrun += f" ORDER BY {DATAKEYSORT[sort]}"
                    sqlrun += ";"
                    results = ExeQuery(sqlrun)
                    #Print out the results formatted using the PrintOutData function
                    PrintOutData(results, userinp)
                    #End the function
                    return 0
                    
                        
#Before running the loop, setup the data spacing dictionary
SetupDataSpacing()


EXITNUM = 6
run = True
while run: #Main loop
    print(f'''\nMake your choice:
1. Print data
2. Search data
3. Update database hours
4. Get total database hours
5. Settings
{EXITNUM}. Exit''')
    #Attempt to make the input an integer, reprompt otherwise
    try:
        inp = int(input("> "))
    except:
        print("Invalid input")
    else:
        if inp == 1:
            HandlePrint()
            print()
        elif inp == 2:
            SearchData()
        elif inp == 3:
            print("Updating...")
            UpdateDatabaseHours()
            print("Database hours updated")
        elif inp == 4:
            print("Fetching data...")
            GetTotalHours()
        elif inp == 5:
            Settings()
        #If the user enters the exit number, break out of the loop and therefore end the program.
        elif inp == EXITNUM:
            run = False
            continue
        #If the user input is out of range, reprompt the user
        else:
            print("Invalid choice")


