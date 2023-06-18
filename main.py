from advEng import *

def main():

    #load player
    player = mainChar("Bedail", "Human")

    #load locations
    locations_file = "locations.json"

    #create environment
    worldEnv = advEngEnv(player, locations_file)
    
    # input loop
    
    worldEnv.playerLook()

    while True:
        userInput = input(player.name + " || " + str(player.hpCurr) + "//" + str(player.hpTotal) + " HP> ")

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
            break
        elif userCmd == "":
            pass
        else:
            print("Command not found!")
        
main()



