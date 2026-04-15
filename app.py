import re
import time
import json
import os
import jsonpickle
import premade_worlds

from models import WorldUpdatePrediction
from prompts import prompt_narrate_current_scene, prompt_world_update, prompt_describe_objective
from config_loader import load_config
from ui import create_and_launch_interface

PATH_GAMELOGS = 'playthroughs/raw'

def clean_json_response(response: str) -> str:
    """Strip markdown code blocks from LLM JSON response if present.
    
    Handles formats like:
    - ```json {...} ```
    - ``` {...} ```
    - Any leading/trailing whitespace and backticks
    """
    response = response.strip()
    
    # Remove markdown code block wrappers
    if response.startswith('```'):
        # Remove starting ``` and optional language identifier (e.g., ```json)
        response = re.sub(r'^```(?:json)?\s*', '', response)
        # Remove ending ```
        response = re.sub(r'\s*```$', '', response)
        response = response.strip()
    
    return response

# Load configuration and initialize models
config_data = load_config()
config = config_data['config']
language = config_data['language']
reasoning_model = config_data['reasoning_model']
narrative_model = config_data['narrative_model']
log_filename = config_data['log_filename']
reasoning_model_name = config_data['reasoning_model_name']
narrative_model_name = config_data['narrative_model_name']

# The game loop
def game_loop(message, history):
    global last_player_position
    global number_of_turns
    global game_log_dictionary
    global starting_narration_for_log
    global previous_answer
    global last_predicted_outcomes
    global last_world_state

    number_of_turns+=1
    game_log_dictionary[number_of_turns] = {}
    game_log_dictionary[number_of_turns]["date"] = time.ctime(time.time())
    
    # For turn 1, include the starting narration; for subsequent turns, include the previous answer
    if number_of_turns == 1:
        game_log_dictionary[number_of_turns]["narration"] = starting_narration_for_log
    else:
        game_log_dictionary[number_of_turns]["narration"] = previous_answer
    
    game_log_dictionary[number_of_turns]["previous_symbolic_world_state"] = jsonpickle.encode(world, unpicklable=False)
    game_log_dictionary[number_of_turns]["previous_rendered_world_state"] = world.render_world(language=language)
    game_log_dictionary[number_of_turns]["user_input"] = message


    answer = ""

    # Get the changes in the world
    system_msg_update, user_msg_update = prompt_world_update(world.render_world(language=language), message, language=language)
    response_update = reasoning_model.prompt_model(system_msg=system_msg_update, user_msg=user_msg_update)

    # Clean any markdown wrappers from the response
    response_update = clean_json_response(response_update)

    # Parse JSON response into Pydantic model
    try:
        world_update = WorldUpdatePrediction.model_validate_json(response_update)
        
        # Show the detected changes in the fictional world
        predicted_outcomes_text = world_update.model_dump_json(indent=2)
        last_predicted_outcomes = f"Player input: {message}\n{predicted_outcomes_text}\n"
        print(f"🛠️ Predicted outcomes of the player input 🛠️\n{last_predicted_outcomes}")
        game_log_dictionary[number_of_turns]["predicted_outcomes"] = predicted_outcomes_text
        
    except Exception as e:
        print(f"Error parsing world update response: {e}")
        print(f"Raw response: {response_update}")
        return "Error processing your input. Please try again."
    
    # World update
    world.update(response_update)
    game_log_dictionary[number_of_turns]["updated_symbolic_world_state"] = jsonpickle.encode(world, unpicklable=True)
    game_log_dictionary[number_of_turns]["updated_rendered_world_state"] = world.render_world(language=language)
    
    if last_player_position is not world.player.location:
        # Narrate new scene
        last_player_position = world.player.location
        system_msg_new_scene, user_msg_new_scene = prompt_narrate_current_scene(
            world.render_world(language=language),
            previous_narrations = world.player.visited_locations[world.player.location.name],
            language=language
            )

        new_scene_narration = narrative_model.prompt_model(system_msg=system_msg_new_scene, user_msg=user_msg_new_scene)
        world.player.visited_locations[world.player.location.name]+=[new_scene_narration] 
        answer += f"\n{new_scene_narration}\n\n"
    else:
        # Narrate actions in the current scene using the narration from the world update
        answer += f"{world_update.narration}\n"


    last_world_state = world.render_world(language=language)
    print(f"\n🌎 World state 🌍\n>Player input: {message}\n{last_world_state}")

    if world.check_objective():
        if language=='es':
            answer += "\n\n🎯¡Completaste el objetivo!"
        else:
            answer += "\n\n🎯You have completed your quest!"
        game_log_dictionary[number_of_turns]["answer"] = answer
    
    # Store the answer for the next turn
    previous_answer = answer

    # Dump the whole gamelog to a json file after this turn
    with open(os.path.join(PATH_GAMELOGS,log_filename), 'w', encoding='utf-8') as f:
        json.dump(game_log_dictionary, f, ensure_ascii=False, indent=4)
    
    return answer.replace("<",r"\<").replace(">", r"\>")

# Instantiate the world
world_id = config["Options"]["WorldID"]
world = premade_worlds.get_world(world_id, language=language)

# Initialize variables
last_player_position = world.player.location
number_of_turns = 0
game_log_dictionary = {}
game_log_dictionary["nickname"] = "anonymous"
game_log_dictionary["language"] = language
game_log_dictionary["world_id"] = world_id
game_log_dictionary["narrative_model_name"] = narrative_model_name
game_log_dictionary["reasoning_model_name"] = reasoning_model_name
starting_narration_for_log = ""
previous_answer = ""
last_predicted_outcomes = ""
last_world_state = ""

print(f"\n🌎 World state 🌍\n{world.render_world(language=language)}\n")

#Generate a description of the starting scene
system_msg_current_scene, user_msg_current_scene = prompt_narrate_current_scene(
    world.render_world(language=language),
    previous_narrations = world.player.visited_locations[world.player.location.name],
    language=language, 
    starting_scene=True
    )
starting_narration_for_log = narrative_model.prompt_model(system_msg=system_msg_current_scene, user_msg=user_msg_current_scene)
world.player.visited_locations[world.player.location.name]+=[starting_narration_for_log]

#Generate a description of the main objective
system_msg_objective, user_msg_objective = prompt_describe_objective(world.objective, language=language)
narrated_objective = narrative_model.prompt_model(system_msg=system_msg_objective, user_msg=user_msg_objective)
try:
    starting_narration_for_log += f"\n\n🎯 {re.findall(r'#([^#]*?)#',narrated_objective)[0]}"
except (IndexError, AttributeError) as e:
    print(f"Error extracting objective: {e}")
    starting_narration_for_log += "\n\n🎯🎯🎯"

with open(os.path.join(PATH_GAMELOGS,log_filename), 'w', encoding='utf-8') as f:
    json.dump(game_log_dictionary, f, ensure_ascii=False, indent=4)

# Instantiate the Gradio app
gradio_interface = create_and_launch_interface(game_loop, starting_narration_for_log)

gradio_interface.launch(inbrowser=False)
