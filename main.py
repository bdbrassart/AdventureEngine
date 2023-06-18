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

        # This runs the command functions if it matches
        if userInput in worldEnv.commands:
            worldEnv.userInput = userInput
            command = worldEnv.commands[userInput]
            command()
        elif userInput.lower() == "exit":
            break
        elif userInput == "":
            pass
        else:
            print("Command not found!")
        
main()



