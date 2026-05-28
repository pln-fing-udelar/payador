"""Loads example worlds from JSON files.

This module provides a simple interface to load pre-configured worlds
from JSON files rather than creating them programmatically.
"""

import os
from utils.world_serializer import load_world_from_json
from world import World


def get_world(arg: str, language: str = 'en') -> World:
    """Load a world from JSON based on the filename or legacy world ID.
    
    Args:
        arg: Either a full filename (e.g., '0_en.json') or legacy world ID ('0', '1', '2', '3')
        language: Language code ('en' or 'es'). Used as fallback for legacy numeric IDs.
    
    Returns:
        A World object loaded from the corresponding JSON file
    """
    # Get the directory where the worlds JSON files are located
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    worlds_dir = os.path.join(current_dir, 'data', 'premade_worlds')
    
    # Check if arg is a full filename or a legacy numeric ID
    if arg.endswith('.json'):
        # New format: full filename (e.g., '0_en.json')
        filename = arg
    else:
        # Legacy format: numeric ID (e.g., '0') - convert using language parameter
        lang_suffix = 'es' if language == 'es' else 'en'
        world_id = arg if arg in ['0', '1', '2', '3'] else '0'
        filename = f"{world_id}_{lang_suffix}.json"
    
    json_path = os.path.join(worlds_dir, filename)
    return load_world_from_json(json_path)
