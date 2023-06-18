

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
    
    def print(self):
        print("Name: " + self.name)
        print("Race: " + self.race)
        print("HP: " + str(self.hpCurr) + " of " + str(self.hpTotal))

class advEngEnv:
    player: mainChar
    commands: dict

    def __init__(self, player):
        self.player = player
        self.commands = {
            "help": self.showHelp,
            "look": self.playerLook,
            "sit": self.playerSit
        }
        
    def showHelp(self):
        self.helpFile = "Lists all available commands."
        print("This is the help command")
    
    def playerLook(self):
        self.helpfile = "Look around the area."
        print("This is the look command")

    def playerSit(self):
        self.helpfile = "Sit down."
        print("This is the sit command")



