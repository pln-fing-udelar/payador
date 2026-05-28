"""Standalone World Manager - CRUD API for managing worlds in data/premade_worlds/"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

# Add parent directory to path so we can import core modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.world_serializer import world_to_dict, dict_to_world, load_world_from_json
from world import World, Location, Item, Character

app = Flask(__name__)
CORS(app)

# Path to premade worlds directory (in parent directory)
WORLDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'premade_worlds')


def get_next_world_id():
    """Scan data/premade_worlds/ and find the next available world ID (integer).
    
    Returns:
        The next available ID as an integer
    """
    if not os.path.exists(WORLDS_DIR):
        return 0
    
    existing_ids = []
    for filename in os.listdir(WORLDS_DIR):
        if filename.endswith('.json'):
            # Extract ID from filename like "0_en.json" or "2_es.json"
            try:
                world_id = int(filename.split('_')[0])
                existing_ids.append(world_id)
            except (ValueError, IndexError):
                pass
    
    if not existing_ids:
        return 0
    return max(existing_ids) + 1


def get_world_files():
    """Get list of all world JSON files in the directory.
    
    Returns:
        List of (id, filename) tuples, sorted by ID
    """
    if not os.path.exists(WORLDS_DIR):
        return []
    
    world_files = []
    for filename in os.listdir(WORLDS_DIR):
        if filename.endswith('.json'):
            try:
                world_id = int(filename.split('_')[0])
                world_files.append((world_id, filename))
            except (ValueError, IndexError):
                pass
    
    return sorted(world_files, key=lambda x: x[0])


@app.route('/')
def index():
    """Serve the world manager HTML page."""
    html_file = os.path.join(os.path.dirname(__file__), 'world_manager.html')
    return send_file(html_file)


@app.route('/api/worlds', methods=['GET'])
def list_worlds():
    """List all worlds with basic metadata."""
    try:
        # Note: language parameter is accepted for frontend compatibility but doesn't filter the list
        request.args.get('language', 'en')
        
        worlds = []
        for world_id, filename in get_world_files():
            filepath = os.path.join(WORLDS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    player_name = data.get('player', {}).get('name', 'Unknown')
                    location_count = len(data.get('locations', []))
                    character_count = len(data.get('characters', []))
                    
                    # Extract language from filename (e.g., "0_en.json" -> "en")
                    language = 'en'
                    if '_' in filename:
                        lang_part = filename.split('_')[1].split('.')[0].lower()
                        if lang_part in ['en', 'es']:
                            language = lang_part
                    
                    worlds.append({
                        'id': world_id,
                        'filename': filename,
                        'player_name': player_name,
                        'location_count': location_count,
                        'character_count': character_count,
                        'language': language
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
        
        return jsonify(worlds), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/worlds', methods=['POST'])
def create_world():
    """Create a new world from form data."""
    try:
        language = request.args.get('language', 'en').lower()
        if language not in ['en', 'es']:
            language = 'en'
        
        data = request.json
        
        # Validate required fields
        if not data.get('player_name') or not data.get('player_location'):
            return jsonify({'error': 'Player name and location are required'}), 400
        
        if not data.get('locations') or len(data['locations']) == 0:
            return jsonify({'error': 'At least one location is required'}), 400
        
        # Convert form data to world dict format
        world_dict = _form_to_world_dict(data)
        
        # Get next ID and save
        world_id = get_next_world_id()
        filename = f"{world_id}_{language}.json"
        filepath = os.path.join(WORLDS_DIR, filename)
        
        # Ensure directory exists
        os.makedirs(WORLDS_DIR, exist_ok=True)
        
        # Write JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(world_dict, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'id': world_id,
            'filename': filename,
            'message': f'World created successfully as {filename}'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/worlds/<int:world_id>', methods=['GET'])
def get_world(world_id):
    """Load a specific world by ID for the requested language."""
    try:
        language = request.args.get('language', 'en').lower()
        if language not in ['en', 'es']:
            language = 'en'
        
        # Find the file with this ID and language
        for fid, filename in get_world_files():
            if fid == world_id and filename.endswith(f'_{language}.json'):
                filepath = os.path.join(WORLDS_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                
                # Convert to form format for editing
                form_data = _world_dict_to_form(world_data)
                return jsonify(form_data), 200
        
        return jsonify({'error': f'World {world_id} not found for language {language}'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/worlds/<int:world_id>', methods=['PUT'])
def update_world(world_id):
    """Update an existing world."""
    try:
        language = request.args.get('language', 'en').lower()
        if language not in ['en', 'es']:
            language = 'en'
        
        data = request.json
        
        # Find the file with this ID and language
        found_filename = None
        for fid, filename in get_world_files():
            if fid == world_id and filename.endswith(f'_{language}.json'):
                found_filename = filename
                break
        
        if not found_filename:
            return jsonify({'error': f'World {world_id} not found for language {language}'}), 404
        
        # Validate
        if not data.get('player_name') or not data.get('player_location'):
            return jsonify({'error': 'Player name and location are required'}), 400
        
        if not data.get('locations') or len(data['locations']) == 0:
            return jsonify({'error': 'At least one location is required'}), 400
        
        # Convert form data to world dict format
        world_dict = _form_to_world_dict(data)
        
        filepath = os.path.join(WORLDS_DIR, found_filename)
        
        # Write updated JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(world_dict, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'id': world_id,
            'filename': found_filename,
            'message': f'World {world_id} updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _form_to_world_dict(form_data):
    """Convert form data to world dictionary format.
    
    Form format: {
        'player_name': str,
        'player_location': str (location id),
        'player_descriptions': [str],
        'locations': [{'id': str, 'name': str, 'descriptions': [str]}],
        'items': [{'id': str, 'name': str, 'descriptions': [str], 'gettable': bool}],
        'characters': [{'id': str, 'name': str, 'descriptions': [str], 'location': str}],
        'objective_first_id': str,
        'objective_first_type': str,
        'objective_second_id': str,
        'objective_second_type': str
    }
    
    Returns:
        Dictionary in world JSON format ready to save to disk
    """
    
    # Build locations list
    locations_data = []
    for loc in form_data.get('locations', []):
        loc_dict = {
            'id': loc.get('id', f"loc_{len(locations_data)}"),
            'name': loc.get('name', ''),
            'descriptions': loc.get('descriptions', []),
            'connecting_locations': loc.get('connecting_locations', []),
            'blocked_locations': loc.get('blocked_locations', {}),
            'items': loc.get('items', [])
        }
        locations_data.append(loc_dict)
    
    # Build items list
    items_data = []
    for item in form_data.get('items', []):
        item_dict = {
            'id': item.get('id', f"item_{len(items_data)}"),
            'name': item.get('name', ''),
            'descriptions': item.get('descriptions', []),
            'gettable': item.get('gettable', True)
        }
        items_data.append(item_dict)
    
    # Build characters list
    characters_data = []
    for char in form_data.get('characters', []):
        char_dict = {
            'id': char.get('id', f"char_{len(characters_data) + 1}"),
            'name': char.get('name', ''),
            'descriptions': char.get('descriptions', []),
            'location': char.get('location', form_data.get('player_location', 'loc_0')),
            'inventory': char.get('inventory', [])
        }
        characters_data.append(char_dict)
    
    # Build player dict
    player_dict = {
        'id': 'char_0',
        'name': form_data.get('player_name', 'Player'),
        'descriptions': form_data.get('player_descriptions', []),
        'location': form_data.get('player_location', 'loc_0'),
        'inventory': []
    }
    
    # Build objective
    objective_data = None
    if form_data.get('objective_first_id') and form_data.get('objective_second_id'):
        objective_data = {
            'first': {
                'type': form_data.get('objective_first_type', 'Item'),
                'id': form_data.get('objective_first_id')
            },
            'second': {
                'type': form_data.get('objective_second_type', 'Character'),
                'id': form_data.get('objective_second_id')
            }
        }
    
    return {
        'locations': locations_data,
        'items': items_data,
        'characters': characters_data,
        'player': player_dict,
        'objective': objective_data
    }


def _world_dict_to_form(world_dict):
    """Convert world dictionary format to form data format.
    
    This is the inverse of _form_to_world_dict for editing existing worlds.
    """
    
    player = world_dict.get('player', {})
    
    form_data = {
        'player_name': player.get('name', ''),
        'player_location': player.get('location', 'loc_0'),
        'player_descriptions': player.get('descriptions', []),
        'locations': world_dict.get('locations', []),
        'items': world_dict.get('items', []),
        'characters': world_dict.get('characters', []),
        'objective_first_id': None,
        'objective_first_type': None,
        'objective_second_id': None,
        'objective_second_type': None
    }
    
    objective = world_dict.get('objective')
    if objective:
        if objective.get('first'):
            form_data['objective_first_id'] = objective['first'].get('id')
            form_data['objective_first_type'] = objective['first'].get('type')
        if objective.get('second'):
            form_data['objective_second_id'] = objective['second'].get('id')
            form_data['objective_second_type'] = objective['second'].get('type')
    
    return form_data


if __name__ == '__main__':
    print(f"Starting World Manager on http://localhost:5001")
    print(f"Worlds directory: {WORLDS_DIR}")
    app.run(debug=True, port=5001)
