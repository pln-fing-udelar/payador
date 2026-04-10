"""Module for serializing and deserializing World objects to/from JSON."""

import json
import os
from typing import Dict, Any
from world import World, Character, Item, Location, Puzzle, Component


def world_to_dict(world: World) -> Dict[str, Any]:
    """Convert a World object to a dictionary suitable for JSON serialization."""
    
    # Collect all items from everywhere (world dict, locations, character inventories)
    all_items_set = set(world.items.values())
    for location in world.locations.values():
        all_items_set.update(location.items)
    for character in world.characters.values():
        all_items_set.update(character.inventory)
    all_items_set.update(world.player.inventory)
    # Also collect items that might be obstacles in blocked passages
    for location in world.locations.values():
        for blocked_loc, obstacle, _ in location.blocked_locations.values():
            if isinstance(obstacle, Item):
                all_items_set.add(obstacle)
    
    # Sort items by name for consistent ordering
    all_items = sorted(all_items_set, key=lambda x: x.name)
    
    # Build ID mappings
    location_id_map = {loc: f"loc_{i}" for i, loc in enumerate(world.locations.values())}
    item_id_map = {item: f"item_{i}" for i, item in enumerate(all_items)}
    # Include player + all NPCs in character ID map
    all_characters = [world.player] + [char for char in world.characters.values()]
    character_id_map = {char: f"char_{i}" for i, char in enumerate(all_characters)}
    
    # Serialize locations
    locations_data = []
    for location_name, location in world.locations.items():
        connecting_location_ids = [location_id_map[loc] for loc in location.connecting_locations]
        
        blocked_locations_data = {}
        for blocked_name, (blocked_loc, obstacle, symmetric) in location.blocked_locations.items():
            blocked_location_id = location_id_map[blocked_loc]
            obstacle_data = _serialize_component(obstacle, location_id_map, item_id_map, character_id_map)
            blocked_locations_data[blocked_location_id] = {
                "obstacle": obstacle_data,
                "symmetric": symmetric
            }
        
        items_ids = [item_id_map[item] for item in location.items]
        
        location_dict = {
            "id": location_id_map[location],
            "name": location.name,
            "descriptions": location.descriptions,
            "connecting_locations": connecting_location_ids,
            "blocked_locations": blocked_locations_data,
            "items": items_ids
        }
        locations_data.append(location_dict)
    
    # Serialize items
    items_data = []
    for item in all_items:
        item_dict = {
            "id": item_id_map[item],
            "name": item.name,
            "descriptions": item.descriptions,
            "gettable": item.gettable
        }
        items_data.append(item_dict)
    
    # Serialize characters
    characters_data = []
    for char_name, character in world.characters.items():
        inventory_ids = [item_id_map[item] for item in character.inventory]
        character_dict = {
            "id": character_id_map[character],
            "name": character.name,
            "descriptions": character.descriptions,
            "location": location_id_map[character.location],
            "inventory": inventory_ids
        }
        characters_data.append(character_dict)
    
    # Serialize player
    player_inventory_ids = [item_id_map[item] for item in world.player.inventory]
    player_dict = {
        "id": character_id_map[world.player],
        "name": world.player.name,
        "descriptions": world.player.descriptions,
        "location": location_id_map[world.player.location],
        "inventory": player_inventory_ids
    }
    
    # Serialize objective
    objective_data = None
    if world.objective:
        obj_first, obj_second = world.objective
        first_type = obj_first.__class__.__name__
        second_type = obj_second.__class__.__name__
        
        first_id = None
        if first_type == "Location":
            first_id = location_id_map[obj_first]
        elif first_type == "Item":
            first_id = item_id_map[obj_first]
        elif first_type == "Character":
            first_id = character_id_map[obj_first]
        
        second_id = None
        if second_type == "Location":
            second_id = location_id_map[obj_second]
        elif second_type == "Item":
            second_id = item_id_map[obj_second]
        elif second_type == "Character":
            second_id = character_id_map[obj_second]
        
        objective_data = {
            "first": {"type": first_type, "id": first_id},
            "second": {"type": second_type, "id": second_id}
        }
    
    return {
        "locations": locations_data,
        "items": items_data,
        "characters": characters_data,
        "player": player_dict,
        "objective": objective_data
    }


def dict_to_world(data: Dict[str, Any]) -> World:
    """Convert a dictionary (from JSON) to a World object."""
    
    # Build reverse ID mappings
    location_map = {}  # ID -> Location object
    item_map = {}  # ID -> Item object
    character_map = {}  # ID -> Character object
    
    # First pass: Create all locations without connections
    for loc_data in data["locations"]:
        location = Location(
            name=loc_data["name"],
            descriptions=loc_data["descriptions"]
        )
        location_map[loc_data["id"]] = location
    
    # First pass: Create all items
    for item_data in data["items"]:
        item = Item(
            name=item_data["name"],
            descriptions=item_data["descriptions"],
            gettable=item_data.get("gettable", True)
        )
        item_map[item_data["id"]] = item
    
    # Second pass: Add items to locations and set up ALL connections (including blocked ones)
    for loc_data in data["locations"]:
        location = location_map[loc_data["id"]]
        
        # Add items to location
        for item_id in loc_data.get("items", []):
            location.items.append(item_map[item_id])
        
        # Add connecting locations
        for connecting_id in loc_data.get("connecting_locations", []):
            location.connecting_locations.append(location_map[connecting_id])
        
        # Also add blocked locations to connecting_locations (temporarily, so they can be blocked)
        for blocked_id in loc_data.get("blocked_locations", {}).keys():
            if location_map[blocked_id] not in location.connecting_locations:
                location.connecting_locations.append(location_map[blocked_id])
    
    # Third pass: Set up blocked passages
    for loc_data in data["locations"]:
        location = location_map[loc_data["id"]]
        
        for blocked_id, blocked_data in loc_data.get("blocked_locations", {}).items():
            blocked_location = location_map[blocked_id]
            obstacle_data = blocked_data["obstacle"]
            symmetric = blocked_data.get("symmetric", True)
            
            # Reconstruct obstacle
            obstacle = _deserialize_component(obstacle_data, location_map, item_map, character_map)
            
            # Block the passage
            location.block_passage(blocked_location, obstacle, symmetric=symmetric)
    
    # First pass: Create all characters without setting inventory
    for char_data in data["characters"]:
        location = location_map[char_data["location"]]
        character = Character(
            name=char_data["name"],
            descriptions=char_data["descriptions"],
            location=location,
            inventory=[]
        )
        character_map[char_data["id"]] = character
    
    # Create player
    player_data = data["player"]
    player_location = location_map[player_data["location"]]
    player = Character(
        name=player_data["name"],
        descriptions=player_data["descriptions"],
        location=player_location,
        inventory=[]
    )
    character_map[player_data["id"]] = player
    
    # Second pass: Add inventory to characters
    for char_data in data["characters"]:
        character = character_map[char_data["id"]]
        for item_id in char_data.get("inventory", []):
            character.inventory.append(item_map[item_id])
    
    # Add inventory to player
    for item_id in player_data.get("inventory", []):
        player.inventory.append(item_map[item_id])
    
    # Create world and add all components
    world = World(player)
    
    for location in location_map.values():
        world.add_location(location)
    
    for item in item_map.values():
        world.add_item(item)
    
    for character in character_map.values():
        if character is not player:  # Don't add player twice
            world.add_character(character)
    
    # Set objective if it exists
    if data.get("objective"):
        obj_data = data["objective"]
        first_type = obj_data["first"]["type"]
        first_id = obj_data["first"]["id"]
        second_type = obj_data["second"]["type"]
        second_id = obj_data["second"]["id"]
        
        first_obj = None
        if first_type == "Location":
            first_obj = location_map[first_id]
        elif first_type == "Item":
            first_obj = item_map[first_id]
        elif first_type == "Character":
            first_obj = character_map[first_id]
        
        second_obj = None
        if second_type == "Location":
            second_obj = location_map[second_id]
        elif second_type == "Item":
            second_obj = item_map[second_id]
        elif second_type == "Character":
            second_obj = character_map[second_id]
        
        world.set_objective(first_obj, second_obj)
    
    return world


def _serialize_component(component: Component, location_map, item_map, character_map) -> Dict[str, Any]:
    """Serialize a component (Item or Puzzle) to a dictionary."""
    comp_type = component.__class__.__name__
    
    if comp_type == "Item":
        return {
            "type": "Item",
            "id": item_map[component]
        }
    elif comp_type == "Puzzle":
        return {
            "type": "Puzzle",
            "name": component.name,
            "descriptions": component.descriptions,
            "problem": component.problem,
            "answer": component.answer
        }
    else:
        raise ValueError(f"Unknown component type: {comp_type}")


def _deserialize_component(data: Dict[str, Any], location_map, item_map, character_map) -> Component:
    """Deserialize a component from a dictionary."""
    comp_type = data["type"]
    
    if comp_type == "Item":
        return item_map[data["id"]]
    elif comp_type == "Puzzle":
        return Puzzle(
            name=data["name"],
            descriptions=data["descriptions"],
            problem=data["problem"],
            answer=data["answer"]
        )
    else:
        raise ValueError(f"Unknown component type: {comp_type}")


def save_world_to_json(world: World, filepath: str) -> None:
    """Save a World object to a JSON file."""
    world_dict = world_to_dict(world)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(world_dict, f, ensure_ascii=False, indent=2)


def load_world_from_json(filepath: str) -> World:
    """Load a World object from a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return dict_to_world(data)
