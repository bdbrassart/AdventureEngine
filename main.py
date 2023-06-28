from advEng import *
import pickle
import time
import threading
import curses
import npcActions

def main(stdscr):

    # Clear the screen and hide the cursor
    stdscr.clear()
    curses.curs_set(0)

    # Enable character echoing
    curses.echo()

    # Enable keypad mode for the input window
    stdscr.keypad(True)

    # Get the dimensions of the terminal window
    maxY, maxX = stdscr.getmaxyx()

    # Calculate the dimensions for the input area and output area
    inputHeight = 1
    outputHeight = maxY - inputHeight

    # Create a subwindow for the input area at the bottom
    inputWin = stdscr.subwin(inputHeight, maxX, maxY - inputHeight, 0)

    # Create a subwindow for the output area
    outputWin = stdscr.subwin(outputHeight, maxX, 0, 0)

    # Enable scrolling for the output area
    outputWin.scrollok(True)

    # Initialize an empty list to store output lines
    outputLines = []

    # Set the prompt for the input area
    prompt = "Enter a command: "

    # We need to prompt the player if they want to start fresh, or load a save.
    outputWin.addstr("    ___       __                 __                  ______            _          \n")
    outputWin.addstr("   /   | ____/ /   _____  ____  / /___  __________  / ____/___  ____ _(_)___  ___ \n")
    outputWin.addstr("  / /| |/ __  / | / / _ \/ __ \/ __/ / / / ___/ _ \/ __/ / __ \/ __ `/ / __ \/ _ \\\n")
    outputWin.addstr(" / ___ / /_/ /| |/ /  __/ / / / /_/ /_/ / /  /  __/ /___/ / / / /_/ / / / / /  __/\n")
    outputWin.addstr("/_/  |_\__,_/ |___/\___/_/ /_/\__/\__,_/_/   \___/_____/_/ /_/\__, /_/_/ /_/\___/ \n")
    outputWin.addstr("                                                             /____/               \n\n")
    outputWin.addstr("Would you like to start a new game or load a save?  Enter 'new' or 'load': ")

    outputWin.refresh()

    startInput = inputWin.getstr().decode('utf-8')

    if startInput == "new":
        #load player
        player = mainChar("Ben", "Human")

        #load locations
        locationsFile = "locations.json"

        #load items
        itemsFile = "items.json"

        #load npcs
        npcFile = "npcs.json"
        
        #create environment
        worldEnv = advEngEnv(player, locationsFile, itemsFile, npcFile, outputWin)

    elif startInput == "load":
        outputWin.addstr("\n\nEnter filename: ")
        outputWin.refresh()
        saveFile = inputWin.getstr().decode('utf-8')
        # load the save file
        with open(saveFile, 'rb') as file:
            worldEnv = pickle.load(file)
        # define the window
        worldEnv.cursesWin = outputWin

    # Clear the output before the main loop starts
    outputWin.clear()
    outputWin.refresh()
    
    # Initialize NPC threads and set some threading variables
    stopEvent = threading.Event()
    event = threading.Event()

    # Inital look
    worldEnv.playerLook()
    outputWin.refresh()

    ## NPC threads are defined in npcActions.py.  We need to loop through each NPC and start their thread.
    allNpcThreads = [] # list of threads for later closing
    for npcID in worldEnv.npcs.keys():
        
        npcFunction = getattr(npcActions, npcID, None)
        npcThread = threading.Thread(target=npcFunction, args=(outputWin,event,stopEvent))
        npcThread.start()
        allNpcThreads.append(npcThread)

    # Main loop
    
    while True:
        # Show prompt
        inputWin.addstr(0, 0, prompt)
        inputWin.refresh()

        #userInput = input(worldEnv.player.name + " || " + str(worldEnv.player.hpCurr) + "//" + str(worldEnv.player.hpTotal) + " HP> ")
        userInput = inputWin.getstr().decode('utf-8')

        # Lower all that shit
        userInput = userInput.lower()

        # Split the input into a command and parameters.  This creates the cmd variable with just the first item, then the remainder are parameters
        inputList = userInput.split(" ")
        userCmd = inputList.pop(0)

        # Scroll the output area if necessary
        if len(outputLines) > outputHeight - 1:
            outputLines = outputLines[-(outputHeight - 1):]

        # Clear the input window for the next input
        inputWin.clear()

        # This runs the command functions if it matches
        if userCmd in worldEnv.commands:
            worldEnv.userCmd = userCmd
            worldEnv.userParams = inputList
            command = worldEnv.commands[userCmd]
            command()
        elif userCmd.lower() == "exit":
            # Stop threads
            stopEvent.set()

            # Notify player
            outputWin.addstr("Killing background threads... \n\n")
            outputWin.refresh()

            # Join all NPC threads
            for thread in allNpcThreads:
                thread.join()

            # Save Prompt
            outputWin.addstr("Would you like to save? (y/n): ")
            outputWin.refresh()
            # Get answer and act accordingly
            savePrompt = inputWin.getstr().decode('utf-8')
            if savePrompt == "y":
                outputWin.addstr("\n\nEnter the name of your save file: ")
                outputWin.refresh()
                filePrompt = inputWin.getstr().decode('utf-8')
                with open(filePrompt, 'wb') as file:
                    # dump save file
                    pickle.dump(worldEnv, file)
            break
        elif userCmd == "":
            pass
        else:
            print("Command not found!")

        # Refresh both windows to update screen
        outputWin.refresh()


curses.wrapper(main)


