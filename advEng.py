
import json
import string

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
        self.locFeatures = loc[0]['locFeatures']

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

class advEngEnv:
    player: mainChar
    commands: dict
    userCmd: str
    userParams: list
    activeLoc: location
    items: dict
    locations: dict

    def __init__(self, player, locations, items):
        # Load the player
        self.player = player
        
        # Load the locations files
        self.locations = self.loadLocations(locations)

        # Load the items files
        self.items = self.loadItems(items)

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
            "drop": self.playerDropItem
        }
    ##########################################
    ### THIS SECTION IS FOR MISC FUNCTIONS ###
    ##########################################

    def formatLocDesc(self, locDesc):
        # get list of features to highlight

        highlightList = self.getFeaturesByLoc(self.currentLoc)

        # create var we can highlight containing the desc
        formattedText = locDesc

        # replace the words from the list with highlighted words
        
        for word in highlightList:
            formattedText = formattedText.replace(word, '\033[33m{}\033[0m'.format(word))
            
        return formattedText.strip()
    
    def formatLocTitle(self, locTitle):
        # Prettify loc title for look
        formattedText = locTitle.center(len(locTitle) + 4)

        formattedText = f"\033[47;30;1m{formattedText}\033[0m"

        return formattedText
    
    def formatLocItems(self, locItems):
        # create list of items for look
        locItemsStr = ', '.join([item.itemName for item in locItems.values()])
        formattedText = f"\033[1mYou also see: \033[0m{locItemsStr}"
        
        return formattedText
    
    def formatLocExits(self, locExits):
        # Create list of exits for look
        locExitsStr = ', '.join(key for item in locExits for key in item.keys())
        formattedText = f"\033[1mExits: \033[0m{locExitsStr}"

        return formattedText
    
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
        for feature in currentLoc.locFeatures:
            for key in feature.keys():
                highlightList.append(key)
        
        return highlightList
        
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
        
        acceptedParams = 2 # the accepted number of params this command accepts, squack if over.
        
        # If the player just typed "look" with no parameters, it's just looking at the room"
        if len(self.userParams) == 0:

            # pull items from item data
            locItems = self.getItemsByLoc(self.player.locID)

            self.currentLoc = self.locations[self.player.locID]

            # Format things prettily
            print("\n")
            print(self.formatLocTitle(self.currentLoc.locTitle))
            print(self.formatLocDesc(self.currentLoc.locDesc))
            print(self.formatLocItems(locItems))
            print(self.formatLocExits(self.currentLoc.locExits))
            print("\n")
        
        # first need to check if any params were entered:

        if len(self.userParams) > 0:

             # if our first parameter is "in", then the player wants to look IN something -- i.e. a feature
            if self.userParams[0] == "in":
                
                # squack if they don't specify a feature to look in
                if self.userParams == 2:
                    print("What would you like to look in?")
                
                # Check if the next parameter is a listed feature
                locFeatures = self.getFeaturesByLoc(self.currentLoc)

                # split up the desc into a list (without punct) so we can see if they're looking in something else in the room and error accordingly
                trans = str.maketrans("", "", string.punctuation)
                noPunct = self.currentLoc.locDesc.translate(trans)
                descWords = noPunct.split()
                
                # first look in valid features to look in
                if self.userParams[1] in locFeatures:
                    # make sure it's a container
                    if self.currentLoc.locFeatures[0][self.userParams[1]][0]['isContainer'] == True:
                        # pull items from featureID
                        featItems = self.getItemsByLoc(self.currentLoc.locFeatures[0][self.userParams[1]][0]['featureID'])
                        # output the magic
                        print(f"Inside the {self.userParams[1]} you see...")
                        for itemDetails in featItems.values():
                            print(itemDetails.itemName)
                    else:
                        print("You can't look in that!")
                    
                elif self.userParams[1] in descWords:
                    print(f"You can't look in that!")
                else:
                    print("I don't see that here!")
            else:
                print("I don't understand!")

        

    def playerSit(self):
        self.name = "sit"
        self.helpfile = "Sit down."
        print("This is the sit command")

    def playerMove(self):
        # Calculate the adjacent locations from locations data
        adjLocs = self.locations[self.player.locID].locExits

        # Determine the destination locID from the input direction
        destLoc = adjLocs[0][self.userCmd]
      
        # Set the players new location
        self.player.locID = destLoc
    
        # Look around
        self.playerLook()
    
    def examine(self): 
        # We can examine features, location items, and inventory items.

        acceptedParams = 1 # the accepted number of params this command accepts, squack if over.

        #Create list of location features to examine
        featureList = []
        for item in self.currentLoc.locFeatures:
            for key in item.keys():
                featureList.append(key)

        #Create list of items to examine
        itemAliasList = {}
        invAliasList = {}
        itemList = self.getItemsByLoc(self.player.locID) # pull all items in location 
        invList = self.getItemsByLoc('locInventory') # pull all inventory items

        # add location item aliases to list
        for itemID, itm in itemList.items():
            itemAliasList[itemID] = itm.itemAlias

        # also add inventory item aliases to list
        for itemID, itm in invList.items():
            invAliasList[itemID] = itm.itemAlias
        
        #print(aliasList)
        if len(self.userParams) > acceptedParams:
            print("I don't understand!")
        elif len(self.userParams) == 0:
            print("What would you like to examine?")
        else:
            # this bit checks if there is a room feature with the proper alias
            if self.userParams[0] in featureList:
                print(self.currentLoc.locFeatures[0][self.userParams[0]][0]['featureDesc'])
                # Now we must activate the container if it has a secret container.
                if self.currentLoc.locFeatures[0][self.userParams[0]][0]['secretContainer'] == True:
                    self.currentLoc.locFeatures[0][self.userParams[0]][0]['isContainer'] = True

            # this bit checks the items in the location
            elif self.userParams[0] in itemAliasList.values():
                for key, value in itemAliasList.items():
                    if self.userParams[0] == value:
                        # if it's just in the location, you only get the description
                        print(self.items[key].itemDesc)
            # this bit checks the items in the player inventory
            elif self.userParams[0] in invAliasList.values():
                for key, value in invAliasList.items():
                    if self.userParams[0] == value:
                        # if you're holding the item, you can examine it closer and get the secret description
                        print(self.items[key].itemDesc)
                        if self.items[key].itemSecret != "":
                            print(self.items[key].itemSecret)        
            else:
                print("I don't see that item here!")
    
    def playerInventory(self):
        
        # pull all inventory items
        playerInventory = self.getItemsByLoc('locInventory')
        
        #print them out pretty
        for itemDetails in playerInventory.values():
            print(itemDetails.itemName)

    def playerGetItem(self):

        acceptedParams = 1 # the accepted number of params this command accepts, squack if over.
        aliasList = {} # create empty dict to store item aliases for later searching
        itemList = self.getItemsByLoc(self.player.locID) # pull all items in location 

        for itemID, itm in itemList.items():
            aliasList[itemID] = itm.itemAlias

        # check and figure out the user input
        if len(self.userParams) > acceptedParams:
            print("I don't understand!")
        elif len(self.userParams) == 0:
            print("What would you like to get?")
        else:
            # if we only have one parameter, continue
            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        print(f"You pick up the {value}.")
                        self.items[key].itemLoc = "locInventory"
            else:
                print("I don't see that item here!")
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
            print("I don't understand!")
        elif len(self.userParams) == 0:
            print("What would you like to get?")
        else:
            # if we only have one parameter, continue
            if self.userParams[0] in aliasList.values():
                # fill the alias dict to compare the user parameter to
                for key, value in aliasList.items():
                    if self.userParams[0] == value:
                        #  if the item exists in the location, change the location to inventory
                        print(f"You drop the {value}.")
                        self.items[key].itemLoc = self.player.locID
            else:
                print("You don't have that item!")
        pass


        
