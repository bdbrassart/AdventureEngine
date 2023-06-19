from advEng import *
import pickle

def main():

    # We need to prompt the player if they want to start fresh, or load a save.

    startPrompt = "Welcome to AdventureEngine.  Would you like to start a new game or load a save?  Enter 'new' or 'load': "

    startInput = input(startPrompt)

    if startInput == "new":
        #load player
        player = mainChar("Bedail", "Human")

        #load locations
        locationsFile = "locations.json"

        #load items
        itemsFile = "items.json"

        #create environment
        worldEnv = advEngEnv(player, locationsFile, itemsFile)
        
    elif startInput == "load":
        #pickle shit here
        saveFile = input("Enter the name of the file you would like to load: ")
        
        with open(saveFile, 'rb') as file:
            worldEnv = pickle.load(file)

    
    # input loop
    
    worldEnv.playerLook()

    while True:
        userInput = input(worldEnv.player.name + " || " + str(worldEnv.player.hpCurr) + "//" + str(worldEnv.player.hpTotal) + " HP> ")

        # Lower all that shit
        userInput = userInput.lower()

        # Split the input into a command and parameters.  This creates the cmd variable with just the first item, then the remainder are parameters
        inputList = userInput.split(" ")
        userCmd = inputList.pop(0)

        # This runs the command functions if it matches
        if userCmd in worldEnv.commands:
            worldEnv.userCmd = userCmd
            worldEnv.userParams = inputList
            command = worldEnv.commands[userCmd]
            command()
        elif userCmd.lower() == "exit":
            #pickle save shit
            savePrompt = input("Would you like to save? (y/n): ")
            if savePrompt == "y":
                filePrompt = input("Enter the name of your save file: ")

                with open(filePrompt, 'wb') as file:
                    pickle.dump(worldEnv, file)
            break
        elif userCmd == "":
            pass
        else:
            print("Command not found!")
        
main()



