"""Loads example worlds from JSON files.

This module provides a simple interface to load pre-configured worlds
from JSON files rather than creating them programmatically.
"""

import os
from world_serializer import load_world_from_json
from world import World


def get_world(arg: str, language: str = 'en') -> World:
    """Load a world from JSON based on the world ID and language.
    
    Args:
        arg: World ID ('0', '1', '2', '3')
        language: Language code ('en' or 'es')
    
    Returns:
        A World object loaded from the corresponding JSON file
    """
    lang_suffix = 'es' if language == 'es' else 'en'
    world_id = arg if arg in ['0', '1', '2', '3'] else '0'
    
    # Get the directory where the worlds JSON files are located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    worlds_dir = os.path.join(current_dir, 'premade_worlds')
    json_path = os.path.join(worlds_dir, f"{world_id}_{lang_suffix}.json")
    
    return load_world_from_json(json_path)