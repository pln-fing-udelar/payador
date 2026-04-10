import gradio as gr
import re
import time
import json
import os
import jsonpickle
import configparser
import premade_worlds

from models import get_llm
from prompts import prompt_narrate_current_scene, prompt_world_update, prompt_describe_objective

PATH_GAMELOGS = 'playthroughs/raw'

# config
config = configparser.ConfigParser()
config.read('config.ini')

# language of the game
language = config['Options']['Language']

# Initialize the model 
reasoning_model_name = config['Models']['ReasoningModel']
narrative_model_name = config['Models']['NarrativeModel']
reasoning_model = get_llm(reasoning_model_name)
narrative_model = get_llm(narrative_model_name)

# Create a name for the log file
timestamp = time.time()
today =  time.gmtime(timestamp)
log_filename =  f"{today[0]}_{today[1]}_{today[2]}_{str(int(time.time()))[-5:]}.json"

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

    # Show the detected changes in the fictional world
    try:
        predicted_outcomes = re.sub(r'#([^#]*?)#','',response_update) 
        last_predicted_outcomes = f"🛠️ Predicted outcomes of the player input 🛠️\n> Player input: {message}\n{predicted_outcomes}\n"
        print(last_predicted_outcomes)
        game_log_dictionary[number_of_turns]["predicted_outcomes"] = predicted_outcomes

    except Exception as e:
        print (f"Error: {e}")
    
    # World update
    world.update(response_update)
    game_log_dictionary[number_of_turns]["updated_symbolic_world_state"] = jsonpickle.encode(world, unpicklable=True)
    game_log_dictionary[number_of_turns]["updated_rendered_world_state"] = world.render_world(language=language)
    
    if last_player_position is not world.player.location:
    #Narrate new scene
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
    #Narrate actions in the current scene
        try:
            answer+= f"{re.findall(r'#([^#]*?)#',response_update)[0]}\n"
        except Exception as e:
            print (f"Error: {e}")


    last_world_state = f"\n🌎 World state 🌍\n>Player input: {message}\n{world.render_world(language=language)}\n"
    print(last_world_state)

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

# Wrapper function for Gradio interface with multiple outputs
def chat_with_display(message, history):
    agent_response = game_loop(message, history)
    return agent_response, last_predicted_outcomes, last_world_state

#Instantiate the Gradio app with custom layout
with gr.Blocks(title="PAYADOR") as gradio_interface:
    gr.Markdown("# PAYADOR")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                height=500,
                value=[{"role": "assistant", "content": starting_narration_for_log.replace("<",r"\<").replace(">", r"\>")}],
                label="Story"
            )
            
        with gr.Column(scale=1):
            predicted_outcomes_display = gr.Textbox(
                label="🛠️",
                interactive=False,
                lines=10
            )
            world_state_display = gr.Textbox(
                label="🌎",
                interactive=False,
                lines=10
            )
    
    textbox = gr.Textbox(
        placeholder="What do you want to do?",
        label="Your Action",
        container=True
    )
    
    # Handle chat submission
    def process_input(message, chat_history):
        if not message:
            return chat_history, "", ""
        
        # Call the game loop and get responses
        agent_response, predicted, world_state = chat_with_display(message, chat_history)
        
        # Update chat history
        chat_history.append({"role": "user", "content": message})
        chat_history.append({"role": "assistant", "content": agent_response})
        
        return chat_history, predicted, world_state
    
    # Submit button triggers the processing
    submit_button = gr.Button("Send", variant="primary")
    submit_button.click(
        fn=process_input,
        inputs=[textbox, chatbot],
        outputs=[chatbot, predicted_outcomes_display, world_state_display]
    ).then(
        lambda: "",
        outputs=textbox
    )
    
    # Allow Enter key to submit
    textbox.submit(
        fn=process_input,
        inputs=[textbox, chatbot],
        outputs=[chatbot, predicted_outcomes_display, world_state_display]
    ).then(
        lambda: "",
        outputs=textbox
    )

gradio_interface.launch(inbrowser=False)
