
import json
import string
import curses
import threading
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

class location:

    #location class that stores information about the current location, so the JSON does not have to be constantly parsed and reparsed.  Populated by the "playerLook" function.
    locID: str
    locTitle: str
    locDesc: str
    locExits: dict
    locFeatures: dict
    locItems: list

    def __init__(self, loc):

        self.locID = loc[0]['locID']
        self.locTitle = loc[0]['locTitle']
        self.locDesc = loc[0]['locDesc']
        self.locExits = loc[0]['locExits']

         # Create the list variable to hold the location objects
        locFeatures = {}
        featureDict = loc[0]['locFeatures'][0]

        # iterate thru the provided locations and create the list of location features

        for featureName, featureDetails in featureDict.items():
            feature = locFeature(featureDetails)
            feature.featureName = featureName
            feature.featureLoc = self.locID
            locFeatures[featureName] = feature
        
        self.locFeatures = locFeatures

class invItem:

    # item class that stores info about items
    itemID: str
    itemLoc: str
    itemName: str
    itemAlias: str
    itemSize: str
    itemDesc: str
    itemSecret: str

    def __init__(self, item):
        self.itemID = item[0]['itemID']
        self.itemLoc = item[0]['itemLoc']
        self.itemName = item[0]['itemName']
        self.itemAlias = item[0]['itemAlias']
        self.itemSize = item[0]['itemSize']
        self.itemDesc = item[0]['itemDesc']
        self.itemSecret = item[0]['itemSecret']

class npChar:

    # npc class stores info about npcs
    npcID: str
    npcLoc: str
    npcName: str
    npcAlias: list
    npcDesc: str
    npcStartLoc: str
    npcPath: list

    def __init__(self, npc):
        self.npcID = npc[0]['npcID']
        self.npcLoc = npc[0]['npcLoc']
        self.npcName = npc[0]['npcName']
        self.npcAlias = npc[0]['npcAlias']
        self.npcDesc = npc[0]['npcDesc']
        self.npcStartLoc = npc[0]['npcStartLoc']
        self.npcPath = npc[0]['npcPath']

class locFeature:
    # class that holds location features so that we can call them like locations and items

    featureID: str
    featureLoc: str
    featureName: str
    featureDesc: str
    featureSecret: str
    isContainer: bool
    secretContainer: bool

    def __init__ (self, feature):
        self.featureID = feature[0]['featureID']
        self.featureDesc = feature[0]['featureDesc']
        self.isContainer = feature[0]['isContainer'] 
        self.secretContainer = feature[0]['secretContainer']

class advEngEnv:
    player: mainChar
    commands: dict
    userCmd: str
    userParams: list
    items: dict
    locations: dict
    npcs: dict
    cursesWin: curses
    allNpcThreads: list
    event: threading.Event
    stopEvent: threading.Event

    def __init__(self, player, locations, items, npcs, cursesWin):
        # Events and other vars for NPC threading
        self.stopEvent = threading.Event()
        self.event = threading.Event()
        self.allNpcThreads = [] # list of threads for later closing

        # Load the player
        self.player = player
        
        # Load the locations files
        self.locations = self.loadLocations(locations)

        # Load the items files
        self.items = self.loadItems(items)

        # Load the npc files
        self.npcs = self.loadNpcs(npcs)
        
        # Set the curses window for display
        self.cursesWin = cursesWin

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
            "examine": self.examine,
            "inventory": self.playerInventory,
            "get": self.playerGetItem,
            "drop": self.playerDropItem,
            "put": self.playerPutItem,
            "say": self.playerSay
        }

        # Define our curses color pairs
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # header color
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK) 
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK) 
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK) 

        # Start the NPC threads
        for npcID in self.npcs.keys():
            npcFunction = getattr(self, npcID, None)
            npcThread = threading.Thread(target=npcFunction, args=(npcID,))
            npcThread.start()
            self.allNpcThreads.append(npcThread)      

    def __getstate__(self):
        # return a dict of class variables to include in save
        state = self.__dict__.copy()
        del state['cursesWin'] # Exclude the curses window, because it doesn't serialize
        return state
    
    def __setstate__(self, state):
        # restore the state from pickle save
        self.__dict__.update(state)
        
    ##########################################
    ### THIS SECTION IS FOR MISC FUNCTIONS ###
    ##########################################

    def formatLocDesc(self, locDesc):
        # get list of features to highlight
        highlightList = self.getFeaturesByLoc(self.currentLoc)
        # create var we can highlight containing the desc
        for word in locDesc.split():
            if word in highlightList:
                self.cursesWin.attrset(curses.color_pair(2))
                self.cursesWin.addstr(f"{word}\x20")
            else:
                self.cursesWin.attrset(curses.A_NORMAL)
                self.cursesWin.addstr(f"{word}\x20")
                
        self.cursesWin.addstr(f"\n")
        
        pass
    
    def formatLocTitle(self, locTitle):
        # Prettify loc title for look
        self.cursesWin.attrset(curses.A_STANDOUT)
        formattedText = locTitle.center(len(locTitle) + 4)
        self.cursesWin.addstr(f"{formattedText}\n")

        pass
    
    def formatLocItems(self, locItems):
        # create list of items for look
        self.cursesWin.attrset(curses.A_BOLD)
        locItemsStr = ', '.join([item.itemName for item in locItems.values()])
        self.cursesWin.addstr(f"You also see: ")
        self.cursesWin.attrset(curses.A_NORMAL)
        self.cursesWin.addstr(f"{locItemsStr}\n")
        
        pass
    
    def formatLocExits(self, locExits):
        # Create list of exits for look
        self.cursesWin.attrset(curses.A_BOLD)
        locExitsStr = ', '.join(key for item in locExits for key in item.keys())
        self.cursesWin.addstr(f"Exits: ")
        self.cursesWin.attrset(curses.A_NORMAL)
        self.cursesWin.addstr(f"{locExitsStr}\n")

        pass
    
    def formatLocNpcs(self, locNpcs):
        # Create list of exits for look
        self.cursesWin.attrset(curses.A_BOLD)
        locNpcStr = ', '.join([npc.npcName for npc in locNpcs.values()])
        self.cursesWin.addstr(f"Also here: ")
        self.cursesWin.attrset(curses.A_NORMAL)
        self.cursesWin.addstr(f"{locNpcStr}\n") 
        
        pass
    
    def getItemsByLoc(self, currentLoc):
        # Returns a list of items in the provided location

        # Create empty list to populate
        itemList = {}
        
        # iterate through items and grab ones in the provided loc
        for itemID, itemDetails in self.items.items():
            if itemDetails.itemLoc == currentLoc:
                itemList[itemID] = itemDetails

        return itemList
    
    def getFeaturesByLoc(self, currentLoc):
        # Returns a list of features in the provided loc.

        # Create list of items to highlight
        highlightList = []

        # Populate it with the item names from the locFeatures 
        for featureName in currentLoc.locFeatures.keys():
            highlightList.append(featureName)
        
        return highlightList
    
    def getNpcsByLoc(self, currentLoc):
        # Returns a list of NPCs in the provided location

        # Create empty list to populate
        npcList = {}
        
        # iterate through npcs and grab ones in the provided loc
        for npcID, npcDetails in self.npcs.items():
            if npcDetails.npcLoc == currentLoc:
                npcList[npcID] = npcDetails

        return npcList
        
    def loadLocations(self, jsonFile):

        # Create the list variable to hold the location objects
        envLocations = {}

        # Load the locations files
        with open(jsonFile, 'r') as file:
            locations = json.load(file)

        # iterate thru the provided locations and create the list of location items
        for locID, locDetails in locations.items():
            loc = location(locDetails)
            envLocations[locID] = loc

        return envLocations
    
    def loadItems(self, jsonFile):

        # Create the list variable to hold the location objects
        envItems = {}

        # Load the locations files
        with open(jsonFile, 'r') as file:
            items = json.load(file)

        # iterate thru the provided locations and create the list of location items
        for itemID, itemDetails in items.items():
            itm = invItem(itemDetails)
            envItems[itemID] = itm

        return envItems
    
    def loadNpcs(self, jsonFile):

        # Create the list variable to hold the npc objects
        envNpcs = {}

        # Load the locations files
        with open(jsonFile, 'r') as file:
            npcs = json.load(file)

        # iterate thru the provided locations and create the list npcs
        for npcID, npcDetails in npcs.items():
            npc = npChar(npcDetails)
            envNpcs[npcID] = npc

        return envNpcs
                
    ###################################     
    ### THIS IS THE COMMAND SECTION ###
    ###################################

    def showHelp(self):
        self.name = "help"
        self.helpFile = "Lists all available commands."
        self.cursesWin.addstr("This is the help command\n\n")
    
    def playerLook(self):
        self.name = "look"
        self.helpfile = "Look around the area."
        
        acceptedParams = 2 # the accepted number of params this command accepts, squack if over.
        
        # If the player just typed "look" with no parameters, it's just looking at the room"
        if len(self.userParams) == 0:

            # pull items from item data
            locItems = self.getItemsByLoc(self.player.locID)
            locNpcs = self.getNpcsByLoc(self.player.locID)

            self.currentLoc = self.locations[self.player.locID]

            # Format things prettily
            #print("\n\n")
            
            self.formatLocTitle(self.currentLoc.locTitle)
            self.formatLocDesc(self.currentLoc.locDesc)
            self.formatLocNpcs(locNpcs)
            self.formatLocItems(locItems)
            self.formatLocExits(self.currentLoc.locExits)
            self.cursesWin.addstr("\n\n")
        
        # first need to check if any params were entered:

        if len(self.userParams) > 0:

             # if our first parameter is "in", then the player wants to look IN something -- i.e. a feature
            if self.userParams[0] == "in":
                
                # squack if they don't specify a feature to look in
                if self.userParams == 2:
                   self.cursesWin.addstr("What would you like to look in?\n\n")
                
                # Check if the next parameter is a listed feature
                locFeatures = self.getFeaturesByLoc(self.currentLoc)

                # split up the desc into a list (without punct) so we can see if they're looking in something else in the room and error accordingly
                trans = str.maketrans("", "", string.punctuation)
                noPunct = self.currentLoc.locDesc.translate(trans)
                descWords = noPunct.split()
                
                # first look in valid features to look in
                if self.userParams[1] in locFeatures:
                    # make sure it's a container
                    if self.currentLoc.locFeatures[self.userParams[1]].isContainer == True:
                        # pull items from featureID
                        featItems = self.getItemsByLoc(self.currentLoc.locFeatures[self.userParams[1]].featureID)
                        # output the magic
                        self.cursesWin.addstr(f"Inside the {self.userParams[1]} you see...\n\n")
                        for itemDetails in featItems.values():
                            self.cursesWin.addstr(itemDetails.itemName)
                    else:
                        self.cursesWin.addstr("You can't look in that!\n\n")
                    
                elif self.userParams[1] in descWords:
                    self.cursesWin.addstr(f"You can't look in that!\n\n")
                else:
                    self.cursesWin.addstr("I don't see that here!\n\n")
            else:
                self.cursesWin.addstr("I don't understand!\n\n")

    def playerSit(self):
        self.name = "sit"
        self.helpfile = "Sit down."
        self.cursesWin.addstr("This is the sit command\n\n")

    def playerMove(self):
        # Calculate the adjacent locations from locations data
        adjLocs = self.locations[self.player.locID].locExits

        if self.userCmd in adjLocs[0].keys():

            # Determine the destination locID from the input direction
            destLoc = adjLocs[0][self.userCmd]

            # Set the players new location
            self.player.locID = destLoc

            # Look around
            self.playerLook()
        
        else:
            self.cursesWin.addstr("You cannot go that way!\n\n")
    
    def examine(self): 
        # We can examine features, location items, and inventory items.

        acceptedParams = 1 # the accepted number of params this command accepts, squack if over.

        #Create list of location features to examine
        featureList = []
        for featureName in self.currentLoc.locFeatures.keys():
            featureList.append(featureName)

        #Create list of items, features, and npcs to examine
        itemAliasList = {}
        invAliasList = {}
        npcAliasList = {}
        itemList = self.getItemsByLoc(self.player.locID) # pull all items in location 
        invList = self.getItemsByLoc('locInventory') # pull all inventory items
        npcList = self.getNpcsByLoc(self.player.locID) # pulls all npcs in location

        # add location item aliases to list
        for itemID, itm in itemList.items():
            itemAliasList[itemID] = itm.itemAlias

        # also add inventory item aliases to list
        for itemID, itm in invList.items():
            invAliasList[itemID] = itm.itemAlias
        
        # add NPC aliases to list
        for npcID, npc in npcList.items():
            npcAliasList[npcID] = npc.npcAlias

        if len(self.userParams) > acceptedParams:
            self.cursesWin.addstr("I don't understand!\n\n")
        elif len(self.userParams) == 0:
            self.cursesWin.addstr("What would you like to examine?\n\n")
        else:
            # this bit checks if there is a room feature with the proper alias
            if self.userParams[0] in featureList:
                self.cursesWin.addstr(self.currentLoc.locFeatures[self.userParams[0]].featureDesc + "\n\n")
                # Now we must activate the container if it has a secret container.
                if self.currentLoc.locFeatures[self.userParams[0]].secretContainer == True:
                    self.currentLoc.locFeatures[self.userParams[0]].isContainer = True

            # this bit checks the items in the location
            elif self.userParams[0] in itemAliasList.values():
                for key, value in itemAliasList.items():
                    if self.userParams[0] == value:
                        # if it's just in the location, you only get the description
                        self.cursesWin.addstr(self.items[key].itemDesc + "\n\n")

            # this bit checks the items in the player inventory
            elif self.userParams[0] in invAliasList.values():
                for key, value in invAliasList.items():
                    if self.userParams[0] == value:
                        # if you're holding the item, you can examine it closer and get the secret description
                        self.cursesWin.addstr(self.items[key].itemDesc)
                        if self.items[key].itemSecret != "":
                            self.cursesWin.addstr(self.items[key].itemSecret + "\n\n")
            
            # this bit checks the npcs in the location
            elif any(self.userParams[0] in value for value in npcAliasList.values()):
                for key, value in npcAliasList.items():
                    if self.userParams[0] in value:
                        # if it's just in the location, you only get the description
                        self.cursesWin.addstr(self.npcs[key].npcDesc + "\n\n")

            else:
               self.cursesWin.addstr("I don't see that item here!\n\n")
    
    def playerInventory(self):
        
        # pull all inventory items
        playerInventory = self.getItemsByLoc('locInventory')
        
        #print them out pretty
        for itemDetails in playerInventory.values():
            self.cursesWin.addstr(itemDetails.itemName)

    def playerGetItem(self):

        acceptedParams = 3 # the accepted number of params this command accepts, squack if over.
        aliasList = {} # create empty dict to store item aliases for later searching

        if len(self.userParams) == 0: # we gotta have some params
            self.cursesWin.addstr("What would you like to get?\n\n")
        elif len(self.userParams) > acceptedParams: # if there are too many params
            self.cursesWin.addstr("I don't understand!\n\n")
        elif len(self.userParams) == 1: # single param means they want to get something from the room
             # pull all items in location 
            itemList = self.getItemsByLoc(self.player.locID)
            
            #build the alias list
            for itemID, itm in itemList.items():
                aliasList[itemID] = itm.itemAlias
            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        self.cursesWin.addstr(f"You pick up the {value}.\n\n")
                        self.items[key].itemLoc = "locInventory"
            else:
                self.cursesWin.addstr("I don't see that item here!\n\n")
        elif self.userParams[1] == "from":
            itemList = self.getItemsByLoc(self.currentLoc.locFeatures[self.userParams[2]].featureID)

            #build the alias list
            for itemID, itm in itemList.items():
                aliasList[itemID] = itm.itemAlias

            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        self.cursesWin.addstr(f"You get the {value} from the {self.userParams[2]}.\n\n")
                        self.items[key].itemLoc = "locInventory"
        pass

    def playerDropItem(self):

        # this is just a copy of the GET command, but instead of putting it in inventory, you put it in the current loc

        acceptedParams = 1 # the accepted number of params this command accepts, squack if over.
        aliasList = {} # create empty dict to store item aliases for later searching
        itemList = self.getItemsByLoc('locInventory') # pull all items in inventory

        for itemID, itm in itemList.items():
            aliasList[itemID] = itm.itemAlias

        # check and figure out the user input
        if len(self.userParams) > acceptedParams:
            self.cursesWin.addstr("I don't understand!\n\n")
        elif len(self.userParams) == 0:
            self.cursesWin.addstr("What would you like to get?\n\n")
        else:
            # if we only have one parameter, continue
            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        self.cursesWin.addstr(f"You drop the {value}.\n\n")
                        self.items[key].itemLoc = self.player.locID
            else:
                self.cursesWin.addstr("You don't have that item!\n\n")
        pass

    def playerPutItem(self):
        acceptedParams = 3 # the accepted number of params this command accepts, squack if over.
        aliasList = {} # create empty dict to store item aliases for later searching

        if len(self.userParams) == 0: # we gotta have some params
           self.cursesWin.addstr("What would you like to get?\n\n")
        elif self.userParams[1] != "in": # if you're not putting something IN something
            self.cursesWin.addstr("I don't understand!\n\n") 
        elif len(self.userParams) > acceptedParams: # if there are too many params
            self.cursesWin.addstr("I don't understand!\n\n")
        else:
            itemList = self.getItemsByLoc('locInventory')

            #build the alias list
            for itemID, itm in itemList.items():
                aliasList[itemID] = itm.itemAlias

            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        self.cursesWin.addstr(f"You put the {value} in the {self.userParams[2]}.\n\n")
                        self.items[key].itemLoc = self.currentLoc.locFeatures[self.userParams[2]].featureID

        pass

    def playerSay(self):
        # Player speaking to the room
        ## Format speech (everything AFTER say command)
        speech = ' '.join(self.userParams) # join all the params as a string
        speech = speech.capitalize() + ".\n\n"# capitalize the first letter
    
        #output the speech to the window
        self.cursesWin.addstr("You say ", curses.color_pair(3))
        self.cursesWin.addstr(speech)

    
    ##################
    ### NPC Actions ###
    ##################
    ## Here we create functions for each NPC, what they do, etc...

    def npcID_1(self, npcID):
        # Reginald Kensington
        while not self.stopEvent.is_set(): 
            if self.player.locID == self.npcs[npcID].npcLoc:
                self.cursesWin.addstr("Reginald says ", curses.color_pair(2))
                self.cursesWin.addstr(f"Good evening, {self.player.name}, how may I be of service today?\n\n")
                self.event.wait(5)           
            else:
                pass

    def npcID_2(self, npcID):
        while not self.stopEvent.is_set():
            if self.player.locID == self.npcs[npcID].npcLoc:
                self.cursesWin.addstr("I'm the valet.\n\n")
            self.event.wait(3)
            self.cursesWin.refresh()



        
