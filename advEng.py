
import json
# Collection of classes for "Adventure Engine"
# please use camelcase

class mainChar:
    name: str
    race: str
    hpTotal: int
    hpCurr: int

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

class advEngEnv:
    player: mainChar
    commands: dict
    userInput: str

    def __init__(self, player, locations):
        # Load the player
        self.player = player
        
        # Load the locations files
        with open(locations, 'r') as file:
            self.locations = json.load(file)

        # Set aliases for commands
        self.commands = {
            "help": self.showHelp,
            "look": self.playerLook,
            "sit": self.playerSit,
            "n": self.playerMove,
            "s": self.playerMove,
            "e": self.playerMove,
            "w": self.playerMove
        }

    ### THIS IS THE COMMAND SECTION
    
    def showHelp(self):
        self.name = "help"
        self.helpFile = "Lists all available commands."
        print("This is the help command")
    
    def playerLook(self):
        self.name = "look"
        self.helpfile = "Look around the area."
        
        # Pull info from locations data
        locTitle = self.locations[self.player.locID][0]['locTitle']
        locDesc = self.locations[self.player.locID][0]['locDesc']
        locExits = self.locations[self.player.locID][0]['locExits']
        locExitsStr = ', '.join(key for item in locExits for key in item.keys())
        # Format things prettily
        print("\n")
        print("\033[1m" + locTitle + "\033[0m")
        print(locDesc)
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
        destLoc = adjLocs[0][self.userInput]
      
        # Set the players new location
        self.player.locID = destLoc
    
        # Look around
        self.playerLook()

