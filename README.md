# AdventureEngine

This is my attempt at building a "game engine" for a text based adventure.

I was inspired by MUDs like Gemstone, DragonRealms, and Aardwolf, and while I realize that I could just go play them instead, since those developers have done amazing work for years and years, I thought it would be fun to try and make a rudimentary "MUD Engine" that you could easily build in your own rooms with just a little JSON.

Maybe eventually you could create a Front End for "dungeon creation" the simplify entry of locations etc..., or potentially build in AI integration with an API?

Primarily it's an excuse to practice python.  I find it a lot easier to learn/play with code if I have an end goal.  I also wanted to get better at understanding classes and other aspects of object oriented programming, so I've tried to explore those a bit here with.

## Classes

### `advEngEnv`
This is the main AdventureEngine environment class.  It stores most of the "game state" information while you're playing the game, including:
- Locations from the `locations.json` file in a `dict`.
- Items from the `items.json` file in a `dict`.
- Player object.
- List of command aliases and their corresponding function in a `dict`.
- User's most recently entered command, and
- Parameters (if any) from aforementioned command.

The `__init__` function loads all the information from the external files and defines the command aliases

The first section is for miscellaneous functions for formatting text, looking up items/locations/features/etc..., or other "non-command" specific functions.

The second section is for the command functions.  These are the ones that are triggered directly by the user with the aliases stored in `advEngEnv.commands` 

### `mainChar`
This stores the information about the character.  Ideally in the future this is where "character sheet" type information will be stored.  Right now it really is only used for a name and current location.  The race and hitpoint variables are there just as placeholders.

### `location`
THis stores information from the `locations.json` file and makes it easier to reference location inforamtion without having to constantly reference the JSON file.

The `__init__` function accepts a single top-level key->value pair from `locations.json` and assigns it to the class variables.

### `invItems` 
This stores information about items in the world.  I went with `invItems` because it got confusing enough referencing the `invItems.item()`, things just got a bit too itemy and confusing.

The `__init__` function accepts a single top-level key->value pair from `items.json` and assigns it to the class variables.

### `locFeature`
This stores information about features in a location.  The `locFeatures` variable of the `location` class contains a dict containing `locFeature` values.  This class is used on the `location` class init function, to hold details about each location's features.

### `npChar`
This stores information about NPC's from the `npcs.json` file.  See more information about NPCs below.

### `advEngEnv`
This is the main environment class for the game.  Variables include:
- `player`: `mainChar` containing the player character.  Defined on init.
- `commands`: Dictionary defined on init that contains command alias-to-function mappings.
- `userCmd`: Most recently entered user command.
- `userParams`: List containing command parameters.
- `items`: Dictionary containing `invItems`.  Defined on init from `items.json`.
- `locations`: Dictionary containing `locations`.  Defined on init from `locations.json`.

The save function dumps this class out, as it contains everything about the current state of the in-progress game.

## JSON Files
For now, there are only two main files that drive the content of the game:

- `locations.json` contains locations and location information.
- `items.json` contains items that a player can interract with that exist at the time of game initialization.
  
### `locations.json`
The structure of the `locations.json` file is as follows:
- Each location is stored in a top-level key, which is a unique location ID.
- The second-level keys are thus:
  - `locID`: This is included in case we need to reference it in the values, instead of the keys.
  - `locTitle`: This acts as the "title" of the room on the console.
  - `locDesc`: Narrative description of the room.  Ideally this is anywhere from 75 to 150 words in length.
  - `locFeatures`: This contains a series of third-level keys are the one-word "alias" of the feature, as referred to by the player.  The values contain information about the feature.
    - `featureID`: The unique featureID, used when a feature is used as a container.
    - `featureDesc`: Narrative description of the feature.
    - `isContainer`: Boolean, if the device is a container.
    - `secretContainer`: Boolean, if the feature is a container, but only after examining the feature.

### `items.json`
The structure of the `items.json` file is as follows:
- Each item is stored in a top-level key, which is a unique item ID.
- The second-level keys are thus:
  - `itemID`: This is included in case we need to reference it in the values, instead of the keys.
  - `itemLoc`: This is the location of the item.
  - `itemName`: The name of the item.  Make sure to use an indefinite article ('a' or 'an') to name items, so that the item list flows narratively.
  - `itemAlias`: This is a one-word alias for an item to be used with commands that refer explicitly to a specific item.
  - `itemSize`: Size of the item.  Not currently in use, but possibly in the future for determining if an item fits in a container.
  - `itemDesc`: Narrative description of the item.  Should be one or two sentences describing a general appearance.
  - `itemSecret`: Only revealed on 'examine,' so only features that would be seen with close examination.

### `npcs.json`
The structure of the `npcs.json` file is as follows:
- Each NPC is stored in a top-level key, which is a unique NPC ID.
- The second-level keys are thus:
  - `npcID`: This is included in case we need to reference it in the values, instead of the keys.
  - `npcLoc`: This is the location of the NPC.  This value can be update/changed when the NPC moves around the world.
  - `npcName`: The name of the NPC.  This would ideally be a full name.
  - `npcAlias`: This is a list of one-word aliases for an NPC to be used with commands that refer explicitly to a specific NPC.
  - `npcDesc`: Narrative description of the NPC.  Should be three or four sentences describing the general appearance of the NPC.
  - `npcStartLoc`: This is the location ID of where the NPC starts when the world environment is created.
  - `npcPath`: This is a list of location IDs that the NPC moves through.  To be used in the NPC functions for roaming.

## Non Player Characters (NPCs)
NPCs are handled a bit cludgy, in my opinion, but it's the only way I could figure out how to handle it.  Each NPC has a function in the `npcActions.py` file that governs the NPCs behavior and actions.  When the game starts, it iterates over the NPCs and starts a thread for each function.  So the NPC function needs to be a loop of all of it's actions and dialog interactions.  It's still a new feature, haven't played with it much but the basis should be there.  This section will contain notes about quirks on programming the NPC functions and some things to avoid and rules to adhere to.

