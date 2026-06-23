"""This module implements the classes needed to represent the fictional world of the game.

The world class includes references to the several components (Items, Locations, Character),
and methods to update according to the detected changes by a language model.
"""

import re
from typing import Type
from models import WorldUpdatePrediction


class Component:
  """A class to represent a component of the world.

  The components considered in the PAYADOR approach are Items, Locations and Characters.
  """
  def __init__ (self, name:str, descriptions: 'list[str]'):

    self.name = name
    """the name of the component"""

    self.descriptions = descriptions
    """a set of natural language descriptions for the component"""
  
class Puzzle (Component):
  """A class to represent a Puzzle"""

  def __init__(self, name:str, descriptions: 'list[str]', problem: str, answer: str):
    
    super().__init__(name, descriptions)
    """inherited from Component"""

    self.problem = problem
    """the main problem to be solved"""

    self.answer = answer
    """a possible answer to the riddle or puzzle"""

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
        self.connecting_locations = [x for x in self.connecting_locations if x is not location]
      else:
        raise Exception(f"Error: A blocked passage to {location.name} already exists")
    else:
        raise Exception(f"Error: Two non-conected locations cannot be blocked")

  def unblock_passage(self, location: 'Location'):
    """Unblock a passage between self and location by adding it to the connecting locations of self.

    In case that the block was symmetric, self will be added to the connecting locations of location.
    """
    if self.blocked_locations[location.name]:
      self.connecting_locations += [location]
      if self.blocked_locations[location.name][2] and self not in location.connecting_locations:
        location.connecting_locations += [self]
      del self.blocked_locations[location.name]
    else:
      raise Exception("Error: That is not a blocked passage")

class Character (Component):
  """A class to represent a character."""
  def __init__ (self, name:str, descriptions: 'list[str]', location:Location, inventory: 'list[Item]' = None):

    super().__init__(name, descriptions)
    """inherited from Component"""

    self.inventory = inventory or []
    """a set of Items the carachter has"""

    self.location = location
    """the location of the character"""

    self.visited_locations = {self.location.name: []}
    """a dictionary that contains the successive descriptions of the visited places"""

  def move(self, new_location: Location):
    """Move the character to a new location."""
    if new_location in self.location.connecting_locations:
      self.location = new_location
      if self.location.name not in self.visited_locations:
        self.visited_locations[self.location.name] = []
    else:
      raise Exception(f"Error: {new_location.name} is not reachable")

  def save_item(self,item: Item, item_location_or_owner):
    """Add an item to the character inventory."""
    if item.gettable:
      if item not in self.inventory:
        self.inventory += [item]
        if item_location_or_owner.__class__.__name__ == 'Character':
          item_location_or_owner.inventory = [i for i in item_location_or_owner.inventory if i != item]
        elif item_location_or_owner.__class__.__name__ == 'Location':
          item_location_or_owner.items = [i for i in item_location_or_owner.items if i != item]
      else:
        raise Exception(f"Error: {item.name} is already in your inventory")
    else:
      raise Exception(f"Error: {item.name} cannot be taken")

  def drop_item (self, item: Item):
    """Leave an item in the current location."""
    self.inventory = [i for i in self.inventory if i != item]
    self.location.items += [item]

  def give_item (self, character: 'Character', item: Item):
    """Give an item to another character."""
    try:
      character.save_item(item, self)
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

    self.objective = None
    """the current objective for the player in this world"""

  def set_objective (self, first_component: Type[Component], second_component: Type[Component]):
    """Set the objective for the world. Valid combinations are:
    - Character with Character
    - Character with (Location or Item)
    - Item with Location
    """
    first_class = first_component.__class__.__name__
    second_class = second_component.__class__.__name__
    
    # Define valid objective combinations
    valid_combinations = {
        ("Character", "Character"),
        ("Character", "Location"),
        ("Location", "Character"),
        ("Character", "Item"),
        ("Item", "Character"),
        ("Item", "Location"),
        ("Location", "Item"),
    }
    
    if (first_class, second_class) in valid_combinations:
        self.objective = (first_component, second_component)
    else:
        raise Exception(f"Error: Cannot set objective with classes {first_class} and {second_class}")

  def check_objective(self) -> bool:
    """Check if the objective has been completed."""
    first = self.objective[0]
    second = self.objective[1]
    first_class = first.__class__.__name__
    second_class = second.__class__.__name__
    
    # Character objectives
    if first_class == "Character":
        if second_class == "Character":
            return first.location == second.location
        elif second_class == "Location":
            return first.location == second
        elif second_class == "Item":
            return second in first.inventory
    
    # Item objectives
    elif first_class == "Item":
        if second_class == "Location":
            return first in second.items
        elif second_class == "Character":
            return first in second.inventory
    
    return False

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

  def render_world(self, *, language:str = 'en', detail_components:bool = True) -> str:
    """Return the fictional world as a natural language description, using simple sentences.

    The components described are only those the player can see in the current location.
    If detail_components is False, then the descriptions for each component are not included.
    """
    rendered_world = ''

    if language == 'es':
      rendered_world = self.__render_world_spanish(detail_components = detail_components)
    else:
      rendered_world = self.__render_world_english(detail_components = detail_components)

    return rendered_world
  
  def __render_world_spanish(self, *,  detail_components:bool = True) -> str:
    """Return the fictional world as a natural language description, using simple sentences in Spanish.

    The components described are only those the player can see in the current location.
    If detail_components is False, then the descriptions for each component are not included.
    """
    player_location = self.player.location
    reachable_locations = [f"<{p.name}>" for p in player_location.connecting_locations]
    blocked_passages = [f"<{p}> bloqueado por <{player_location.blocked_locations[p][1].name}>" for p in player_location.blocked_locations.keys()]
    characters_in_the_scene = [character for character in self.characters.values() if character.location is player_location]

    
    world_description = f'El jugador está en <{player_location.name}>\n'
    
    if reachable_locations:
      world_description += f'Desde <{player_location.name}> el jugador puede ir a: {(", ").join(reachable_locations)}\n'
    else:
      world_description += f'Desde <{player_location.name}> el jugador puede ir a: None\n'

    if blocked_passages:
      world_description += f'Desde <{player_location.name}> hay pasajes bloqueados hacia: {(", ").join(blocked_passages)}\n'
    else:
      world_description += f'Desde <{player_location.name}> hay pasajes bloqueados hacia: None\n'

    if self.player.inventory:
      world_description += f'El jugador tiene los siguientes objetos en su inventario: {(", ").join([f"<{i.name}>" for i in self.player.inventory])}\n'
    else:
      world_description += f'El jugador tiene los siguientes objetos en su inventario: None\n'

    if player_location.items:
      world_description += f'El jugador puede ver los siguientes objetos: {(", ").join([f"<{i.name}>" for i in player_location.items])}\n'
    else:
      world_description += f'El jugador puede ver los siguientes objetos: None\n'
      
    if characters_in_the_scene:
      world_description += f'El jugador puede ver a los siguientes personajes: {(", ").join([f"<{c.name}>" for c in characters_in_the_scene])}'
    else:
      world_description += f'El jugador puede ver a los siguientes personajes: None'

    details = ""
    if detail_components:
      items_in_the_scene = player_location.items + self.player.inventory + [blocked_values[1] for blocked_values in player_location.blocked_locations.values() if isinstance(blocked_values[1], Item)]
      puzzles_in_the_scene = [blocked_values[1] for blocked_values in player_location.blocked_locations.values() if isinstance(blocked_values[1], Puzzle)]

      details += "\nAquí hay una descripción de cada componente.\n"
      details += f"<{player_location.name}>: Este es el lugar en el que está el jugador. {('. ').join(player_location.descriptions)}.\n"
      details += "Personajes:\n"
      details += f"- <Jugador>: El jugador está actuando como <{self.player.name}>. {('. ').join(self.player.descriptions)}.\n"
      if len(characters_in_the_scene)>0:
        for character in characters_in_the_scene:
          details += f"- <{character.name}>: {('. ').join(character.descriptions)}."
          if len(character.inventory)>0:
            details += f"Este personaje tiene los siguientes objetos en su inventario: {(', ').join([f'<{i.name}>' for i in character.inventory])}\n"
            items_in_the_scene+= character.inventory
          else:
            details += "\n"
      if len(items_in_the_scene)>0:
        details+="Objetos:\n"
        for item in items_in_the_scene:
          details += f"- <{item.name}>: {('. ').join(item.descriptions)}\n"
      if len(puzzles_in_the_scene)>0:
        details+="Puzzles:\n"
        for puzzle in puzzles_in_the_scene:
          details+= f'- <{puzzle.name}>: {(". ").join(puzzle.descriptions)}. El acertijo a resolver es: "{puzzle.problem}". La respuesta esperada, que NO PUEDES decirle al jugador (JAMÁS) es: "{puzzle.answer}".\n'

    return world_description + '\n' + details

  def __render_world_english(self, *,  detail_components:bool = True) -> str:
    """Return the fictional world as a natural language description, using simple sentences in English.

    The components described are only those the player can see in the current location.
    If detail_components is False, then the descriptions for each component are not included.
    """
    player_location = self.player.location
    reachable_locations = [f"<{p.name}>" for p in player_location.connecting_locations]
    blocked_passages = [f"<{p}> blocked by <{player_location.blocked_locations[p][1].name}>" for p in player_location.blocked_locations.keys()]
    characters_in_the_scene = [character for character in self.characters.values() if character.location is player_location]

    
    world_description = f'The player is in <{player_location.name}>\n'
    
    if reachable_locations:
      world_description += f'From <{player_location.name}> the player can access: {(", ").join(reachable_locations)}\n'
    else:
      world_description += f'From <{player_location.name}> the player can access: None\n'

    if blocked_passages:
      world_description += f'From <{player_location.name}> there are blocked passages to: {(", ").join(blocked_passages)}\n'
    else:
      world_description += f'From <{player_location.name}> there are blocked passages to: None\n'

    if self.player.inventory:
      world_description += f'The player has the following objects in the inventory: {(", ").join([f"<{i.name}>" for i in self.player.inventory])}\n'
    else:
      world_description += f'The player has the following objects in the inventory: None\n'

    if player_location.items:
      world_description += f'The player can see the following objects: {(", ").join([f"<{i.name}>" for i in player_location.items])}\n'
    else:
      world_description += f'The player can see the following objects: None\n'
      
    if characters_in_the_scene:
      world_description += f'The player can see the following characters: {(", ").join([f"<{c.name}>" for c in characters_in_the_scene])}'
    else:
      world_description += f'The player can see the following characters: None'

    details = ""
    if detail_components:
      items_in_the_scene = player_location.items + self.player.inventory + [blocked_values[1] for blocked_values in player_location.blocked_locations.values() if isinstance(blocked_values[1], Item)]
      puzzles_in_the_scene = [blocked_values[1] for blocked_values in player_location.blocked_locations.values() if isinstance(blocked_values[1], Puzzle)]

      details += "\nHere is a description of each component.\n"
      details += f"<{player_location.name}>: This is the player's location. {('. ').join(player_location.descriptions)}.\n"
      details += "Characters:\n"
      details += f"- <Player>: The player is acting as <{self.player.name}>. {('. ').join(self.player.descriptions)}.\n"
      if len(characters_in_the_scene)>0:
        for character in characters_in_the_scene:
          details += f"- <{character.name}>: {('. ').join(character.descriptions)}."
          if len(character.inventory)>0:
            details += f" This character has the following items: {(', ').join([f'<{i.name}>' for i in character.inventory])}\n"
            items_in_the_scene+= character.inventory
          else:
            details += "\n"
      if len(items_in_the_scene)>0:
        details+="Objects:\n"
        for item in items_in_the_scene:
          details += f"- <{item.name}>: {('. ').join(item.descriptions)}\n"
      if len(puzzles_in_the_scene)>0:
        details+="Puzzles:\n"
        for puzzle in puzzles_in_the_scene:
          details+= f'- <{puzzle.name}>: {(". ").join(puzzle.descriptions)}. The riddle to solve is: "{puzzle.problem}". The expected answer, that you CANNOT tell the player (EVER) is: "{puzzle.answer}".\n'

    return world_description + '\n' + details

  def update (self, updates: str) -> None:
    """Does the changes in the world according to the output of the language model.

    The considered transformations are:
      - moved items
      - unblocked locations
      - player movement
      
    Args:
      updates: JSON string from LLM containing structured world update prediction
    """
    try:
      # Parse JSON response into Pydantic model
      world_update = WorldUpdatePrediction.model_validate_json(updates)
      
      # Process moved items
      for moved_object in world_update.moved_items:
        self._process_moved_object(moved_object.name, moved_object.destination)
      
      # Process unblocked locations
      for passage in world_update.unblocked_locations:
        try:
          self.locations[self.player.location.name].unblock_passage(self.locations[passage])
        except Exception as e:
          print(f"Error unblocking passage '{passage}': {e}")
      
      # Process player movement
      if world_update.player_movement is not None:
        try:
          self.player.move(self.locations[world_update.player_movement])
        except Exception as e:
          print(f"Error moving player to '{world_update.player_movement}': {e}")
    
    except Exception as e:
      print(f"Error parsing world update: {e}")

  def _process_moved_object(self, object_name: str, destination: str) -> None:
    """Process a single moved object.
    
    Handles cases where items are moved between inventory/locations,
    initiated by either the player or NPCs.
    
    Possible transitions:
      - Character/Location → Player's inventory
      - Character/Location → Other character's inventory
      - Character/Location → Location
    """
    try:
      world_item = self.items[object_name]
      
      # Find current location of item
      current_location = None
      
      # Check if in player inventory
      if world_item in self.player.inventory:
        current_location = ('inventory', self.player)
      else:
        # Check if in any NPC's inventory
        for character in self.characters.values():
          if world_item in character.inventory:
            current_location = ('inventory', character)
            break
        # Check if in any location
        if not current_location:
          for location in self.locations.values():
            if world_item in location.items:
              current_location = ('location', location)
              break
      
      if not current_location:
        print(f"Error: Item '{object_name}' not found anywhere in the world")
        return
      
      current_type, current_holder = current_location
      
      # Case 1: Item moved to player's inventory
      if destination in ['Inventory', 'Inventario', 'Player', 'Jugador', self.player.name]:
        if current_type == 'inventory':
          # Someone (player or NPC) is giving to player
          current_holder.inventory = [i for i in current_holder.inventory if i != world_item]
          self.player.inventory.append(world_item)
        elif current_type == 'location':
          # Item in location, player (or someone) takes it
          current_holder.items = [i for i in current_holder.items if i != world_item]
          self.player.inventory.append(world_item)
      
      # Case 2: Item moved to a character's inventory
      elif destination in self.characters:
        target_character = self.characters[destination]
        if current_type == 'inventory':
          current_holder.inventory = [i for i in current_holder.inventory if i != world_item]
          target_character.inventory.append(world_item)
        elif current_type == 'location':
          current_holder.items = [i for i in current_holder.items if i != world_item]
          target_character.inventory.append(world_item)
      
      # Case 3: Item dropped at a location
      elif destination in self.locations:
        target_location = self.locations[destination]
        if current_type == 'inventory':
          current_holder.inventory = [i for i in current_holder.inventory if i != world_item]
          target_location.items.append(world_item)
        elif current_type == 'location':
          current_holder.items = [i for i in current_holder.items if i != world_item]
          target_location.items.append(world_item)
    
    except Exception as e:
      print(f"Error processing moved object '{object_name}' to '{destination}': {e}")

