"""This module implements the classes needed to represent the fictional world of the game.

The world class includes references to the several components (Items, Locations, Character),
and methods to update according to the detected changes by a language model.
"""

import re


class Component:
  """A class to represent a component of the world.

  The components considered in the PAYADOR approach are Items, Locations and Characters.
  """
  def __init__ (self, name:str, descriptions: 'list[str]'):

    self.name = name
    """the name of the component"""

    self.descriptions = descriptions
    """a set of natural language descriptions for the component"""

class Item (Component):
  """A class to represent an Item."""
  def __init__ (self, name:str, descriptions: 'list[str]', gettable: bool = True):

    super().__init__(name, descriptions)
    """inherited from Component"""

    self.gettable = gettable
    """indicates if the Item can be taken by the player"""

class Location (Component):
  """A class to represent a Location in the world."""
  def __init__ (self, name:str, descriptions: 'list[str]', items: 'list[Item]' = None, connecting_locations: 'list[Location]' = None):

    super().__init__(name, descriptions)
    """inherited from Component"""

    self.items = items or []
    """a list of the items available in that location"""

    self.connecting_locations = connecting_locations or []
    """a list of the reachable locations from itself."""

    self.blocked_locations = {}
    """a dictionary with the name of a location as key and <location,obstacle,symmetric> as value.
    A blocked passage between self and a location means that it
    will be reachable from [self] after overcoming the [obstacle].
    The symmetric variable is a boolean that indicates if, when unblocked,
    [self] will also be reachable from [location].
    """

  def block_passage(self, location: 'Location', obstacle, symmetric: bool = True):
    """Block a passage between self and location using an obstacle."""
    if location in self.connecting_locations:
      if location.name not in self.blocked_locations:
        self.blocked_locations[location.name] = (location, obstacle, symmetric)
      else:
        raise Exception(f"Error: A blocked passage to {location.name} already exists")
    else:
        raise Exception(f"Error: Two non-conected locations cannot be blocked")

  def unblock_passage(self, location: 'Location'):
    """Unblock a passage between self and location by adding it to the connecting locations of self.

    In case that the block was symmetric, self will be added to the connecting locations of location.
    """
    self.connecting_locations += [location]
    if self.blocked_locations[location.name][2]:
      location.connecting_locations += [self]
    del self.blocked_locations[location.name]

class Character (Component):
  """A class to represent a character."""
  def __init__ (self, name:str, descriptions: 'list[str]', location:Location, inventory: 'list[Item]' = None):

    super().__init__(name, descriptions)
    """inherited from Component"""

    self.inventory = inventory or []
    """a set of Items the carachter has"""

    self.location = location
    """the location of the character"""

  def move(self, new_location: Location):
    """Move the character to a new location."""
    if new_location in self.location.connecting_locations:
      self.location = new_location
    else:
      raise Exception(f"Error: {new_location.name} is not reachable")

  def save_item(self,item: Item):
    """Add an item to the character inventory."""
    if item.gettable:
      if item not in self.inventory:
        self.inventory += [item]
        self.location.items = [i for i in self.location.items if i is not item]
      else:
        raise Exception(f"Error: {item.name} is already in your inventory")
    else:
      raise Exception(f"Error: {item.name} cannot be taken")

  def drop_item (self, item: Item):
    """Leave an item in the current location."""
    self.inventory = [i for i in self.inventory if i is not item]
    self.location.items += [item]

  def give_item (self, character: 'Character', item: Item):
    """Give an item to another character."""
    try:
      self.inventory = [i for i in self.inventory if i is not item]
      character.save_item(item)
    except Exception as e:
      print(e)


class World:
  """A class to represent the fictional world, with references to every component."""
  def __init__ (self, player: Character) -> None:

    self.items = {}
    """a dictionary of all the Items in the world, with their names as values"""

    self.characters = {}
    """a dictionary of all the Characters in the world, with their names as values"""

    self.locations =  {}
    """a dictionary of all the Locations in the world, with their names as values"""

    self.player = player
    """a character for the player"""

  def add_location (self,location: Location) -> None:
    """Add a location to the world."""
    if location.name in self.locations:
      raise Exception(f"Error: Already exists a location called '{location.name}'")
    else:
       self.locations[location.name] = location

  def add_item (self, item: Item) -> None:
    """Add an item to the world."""  
    if item.name in self.items:
      raise Exception(f"Error: Already exists an item called '{item.name}'")
    else:
      self.items[item.name] = item

  def add_character (self, character: Character) -> None:
    """Add a character to the world."""
    if character.name in self.characters:
      raise Exception(f"Error: Already exists a character called '{character.name}'")
    else:
      self.characters[character.name] = character

  def add_locations (self,locations: 'list[Location]') -> None:
    """"Add a set of locations to the world."""
    for location in locations:
      self.add_location(location)

  def add_items (self, items: 'list[Item]') -> None:
    """Add a set of items to the world."""
    for item in items:
      self.add_item(item)

  def add_characters (self, characters: 'list[Character]') -> None:
    """Add a set of characters to the world."""
    for character in characters:
      self.add_character(character)

  def render_world(self, *,  detail_components:bool = True) -> str:
    """Return the fictional world as a natural language description, using simple sentences.

    The components described are only those the player can see in the current location.
    If detail_components is False, then the descriptions for each component are not included.
    """
    player_location = self.player.location

    world_description = f'You are in <{player_location.name}>\n'
    world_description += f'From <{player_location.name}> you can access: {(", ").join([f"<{p.name}>" for p in player_location.connecting_locations])}\n'
    world_description += f'From <{player_location.name}> there are blocked passages to: {(", ").join([f"<{p}> blocked by <{player_location.blocked_locations[p][1].name}>" for p in player_location.blocked_locations.keys()])}\n'
    world_description += f'You have the following items in your inventory: {(", ").join([f"<{i.name}>" for i in self.player.inventory])}\n'
    world_description += f'If you look around, you can see: {(", ").join([f"<{i.name}>" for i in player_location.items])}\n'

    other_characters = [f"<{c_name}>" for c_name in self.characters
                        if self.characters[c_name].location is player_location]
    if other_characters:
      world_description += f'You can also see some people: {(", ").join(other_characters)}'

    details = ""
    if detail_components:
      items_in_the_scene = player_location.items + self.player.inventory + [blocked_values[1] for blocked_values in player_location.blocked_locations.values() if isinstance(blocked_values[1], Item)]
      characters_in_the_scene = [character for character in self.characters.values() if character.location is player_location]

      details += "\nHere is a description of each component.\n"
      details += f"<{player_location.name}>: This is the player's location. {('. ').join(player_location.descriptions)}.\n"
      details += "Characters:\n"
      details += f"- <Player>: The player is acting as {self.player.name}. {('. ').join(self.player.descriptions)}.\n"
      if len(characters_in_the_scene)>0:
        for character in characters_in_the_scene:
          details += f"- <{character.name}>: {('. ').join(character.descriptions)}."
          if len(character.inventory)>0:
            details += f" This character has the following items: {(', ').join([f'<{i.name}>' for i in character.inventory])}\n"
            items_in_the_scene+= character.inventory
      if len(items_in_the_scene)>0:
        details+="Objects:\n"
        for item in items_in_the_scene:
          details += f"- <{item.name}>: {('. ').join(item.descriptions)}\n"

    return world_description + '\n' + details

  def parse_updates (self, updates: str) -> None:
    """Does the changes in the world according to the output of the language model.

    The possible changes considered are:
      - an object was moved
      - a location is now reachable
      - the position of the player changed.
    """
    self.parse_moved_objects(updates)
    self.parse_blocked_passages(updates)
    self.parse_location_change(updates)

  def parse_moved_objects (self, updates: str) -> None:
    """Parse the output of the language model to update the position of objects.

    There are three cases:
      - the player has a new item
      - the player gave an item to other character
      - the player dropped an item.
    """
    parsed_objects = re.findall(r".*Moved object:\s*(.+)",updates)
    if 'None' not in parsed_objects:
      parsed_objects_split = re.findall(r"<[^<>]*?>.*?<[^<>]*?>",parsed_objects[0])
      for parsed_object in parsed_objects_split:
        pair = re.findall(r"<([^<>]*?)>.*?<([^<>]*?)>",parsed_object)
        try:
          world_item = self.items[pair[0][0]]
          if pair[0][1] == 'Inventory': #(save_item case)
            self.player.save_item(world_item)
          elif pair[0][1] in self.characters: #(give_item case)
            self.player.give_item(self.characters[pair[0][1]], world_item)
          else: #(drop_item case)
            self.player.drop_item(world_item)
        except Exception as e:
          print(e)

  def parse_blocked_passages (self, updates: str) -> None:
    """Parse the output of the language model to update the reachable locations."""
    parsed_blocked_passages = re.findall(r".*Blocked passages now available:\s*(.+)",updates)
    if 'None' not in parsed_blocked_passages:
      parsed_blocked_passages_split = re.findall(r"<([^<>]*?)>",parsed_blocked_passages[0])
      for parsed_passage in parsed_blocked_passages_split:
        try:
          self.locations[self.player.location.name].unblock_passage(self.locations[parsed_passage])
        except Exception as e:
          print (e)

  def parse_location_change (self, updates: str) -> None:
    """Parse the output of the language model to update the position of the player."""
    parsed_location_change = re.findall(r".*Your location changed: (.+)",updates)
    if "None" not in parsed_location_change:
      parsed_location_change_split = re.findall(r"<([^<>]*?)>",parsed_location_change[0])
      try:
        self.player.move(self.locations[parsed_location_change_split[0]])
      except Exception as e:
        print(e)

