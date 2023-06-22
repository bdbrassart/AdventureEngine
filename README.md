# AdventureEngine

This is just a small "game engine" that could act as a framework for a text based adventure.

I was inspired by MUDs like Gemstone, DragonRealms, and Aardwolf, and while I realize that I could just go play them instead, I thought it would be fun to try and make a rudimentary "MUD Engine" that you could easily build in your own rooms without much coding.

Maybe eventually you could create a Front End for "dungeon creation" the simplify entry of locations etc...

Primarily it's an excuse to practice python.  I find it a lot easier to learn/play with code if I have an end goal.  I also wanted to get better at understanding classes and other aspects of object oriented programming.

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

## JSON Files

### locations.json
The structure of the `locations.json` file is as follows:
- Each location is stored in a top-level key, which is a unique location ID.
- The second-level keys are thus:
  - `locID`: This is included in case we need to reference it in the values, instead of the keys.
  - `locTitle`: This acts as the "title" of the room on the console.
  - `locDesc`: Narrative description of the room.  Ideally this is anywhere from 75 to 150 words in length.
  - `locFeatures`: This contains a serie s of third-level keys are the one-word "alias" of the feature, as referred to by the player.  The values contain information about the feature.
    - `featureID`: The unique featureID, used when a feature is used as a container.
    - `featureDesc`: Narrative description of the feature.
    - `isContainer`: Boolean, if the device is a container.
    - `secretContainer: Boolean, if the feature is a container, but only after examining the feature.

### items.json
location == room

locations are defined in "locations.json" and include multiple parts, including title, description, and features.

feature == part of a location that is permanent to the location

item == something you can take with you from the room.  Items are defined in 'items.json'

