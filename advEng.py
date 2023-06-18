
import json
# Collection of classes for "Adventure Engine"
# please use camelcase

class mainChar:
    name: str
    race: str
    hpTotal: int
    hpCurr: int
    inventory: dict

    def __init__(self, name, race):
        self.name = name
        self.race = race
        self.hpTotal = 20
        self.hpCurr = 20
        self.locID = "locID_1"
    
    def print(self):
        print("Name: " + self.name)
        print("Race: " + self.race)
        print("HP: " + str(self.hpCurr) + " of " + str(self.hpTotal))

class location:

    #location class that stores information about the current location, so the JSON does not have to be constantly parsed and reparsed.  Populated by the "playerLook" function.

    locTitle: str
    locDesc: str
    locExits: dict
    locFeatures: dict

    def __init__(self, title, desc, exits, features):
        self.locTitle = title
        self.locDesc = desc
        self.locExits = exits
        self.locFeatures = features
        

class advEngEnv:
    player: mainChar
    commands: dict
    userCmd: str
    userParams: list
    activeLoc: location

    def __init__(self, player, locations):
        # Load the player
        self.player = player
        
        # Load the locations files
        with open(locations, 'r') as file:
            self.locations = json.load(file)

        # set the params so it's not empty
        self.userParams = []

        # Set aliases for commands
        self.commands = {
            "help": self.showHelp,
            "look": self.playerLook,
            "sit": self.playerSit,
            "n": self.playerMove,
            "s": self.playerMove,
            "e": self.playerMove,
            "w": self.playerMove,
            "examine": self.examine
        }
    ##########################################
    ### THIS SECTION IS FOR MISC FUNCTIONS ###
    ##########################################

    def formatRoomDesc(self, inputText):
        # Create list of items to highlight
        highlightList = []

        # Populate it with the item names from the locItems 
        for feature in self.currentLoc.locFeatures:
            for key in feature.keys():
                highlightList.append(key)
        
        formattedText = ""

        for word in inputText.split():
            if word in highlightList:
                formattedText += f"\033[33m{word}\033[0m " # Apply the highlighting to the word
            else: 
                formattedText += f"{word} " # Don't apply highlighting
            
        return formattedText.strip()
    
    def formatRoomTitle(self, inputText):
        formattedText = inputText.center(len(inputText) + 4)

        formattedText = f"\033[47;30;1m{formattedText}\033[0m"

        return formattedText
    
    ###################################     
    ### THIS IS THE COMMAND SECTION ###
    ###################################

    def showHelp(self):
        self.name = "help"
        self.helpFile = "Lists all available commands."
        print("This is the help command")
    
    def playerLook(self):
        self.name = "look"
        self.helpfile = "Look around the area."
        
        # If we think the player wants to examine an item, suggest that
        if len(self.userParams) > 0:
            paramStr = ' '.join(self.userParams)
            print(f"You might want to EXAMINE the {paramStr}")
            return

        # Pull info from locations data
        
        locTitle = self.locations[self.player.locID][0]['locTitle']
        locDesc = self.locations[self.player.locID][0]['locDesc']
        locItems = self.locations[self.player.locID][0]['locItems']
        locExits = self.locations[self.player.locID][0]['locExits']
        locExitsStr = ', '.join(key for item in locExits for key in item.keys())

        self.currentLoc = location(locTitle, locDesc, locExits, locItems)

        # Format things prettily
        print("\n")
        print(self.formatRoomTitle(self.currentLoc.locTitle))
        print(self.formatRoomDesc(self.currentLoc.locDesc))
        print("\033[1mExits: \033[0m" + locExitsStr)
        print("\n")
        

    def playerSit(self):
        self.name = "sit"
        self.helpfile = "Sit down."
        print("This is the sit command")

    def playerMove(self):
        # Calculate the adjacent locations from locations data
        adjLocs = self.locations[self.player.locID][0]['locExits']

        # Determine the destination locID from the input direction
        destLoc = adjLocs[0][self.userCmd]
      
        # Set the players new location
        self.player.locID = destLoc
    
        # Look around
        self.playerLook()
    
    def examine(self): 
        acceptedParams = 1 # the accepted number of params this command accepts, squack if over.

        #Create list of items in the room to examine
        itemList = []

        for item in self.currentLoc.locFeatures:
            for key in item.keys():
                itemList.append(key)

        if len(self.userParams) > acceptedParams:
            print("I don't understand!")
        elif len(self.userParams) == 0:
            print("What would you like to examine?")
        else:
            if self.userParams[0] in itemList:
                print(self.currentLoc.locFeatures[0][self.userParams[0]][0]['featureDesc'])
            else:
                print("I don't see that item here!")
        pass

