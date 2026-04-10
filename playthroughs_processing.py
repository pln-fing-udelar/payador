import json
import os
import time
import re
import numpy

PATH_PLAYTHROUGHS = 'playthroughs/'

def ignored_playthroughs_list (path_to_file: str):
    ignored_playthroughs = []
    with open(path_to_file, 'r') as f:
        for line in f:
            ignored_playthroughs += [line.replace('\n','')]
    return ignored_playthroughs

def get_elapsed_time(starting_turn: str, ending_turn: str, playthrough: dict) -> time.localtime:
    starting_time = time.mktime(time.strptime((playthrough[starting_turn]["date"])))
    ending_time = time.mktime(time.strptime((playthrough[ending_turn]["date"])))

    return ending_time-starting_time

def get_turns_to_complete_objective(playthrough: dict) -> int:
    max_turns = int(list(playthrough.keys())[-1]) + 1
    index = 1
    found = False

    while not found and index < max_turns:
        if  "🎯" in playthrough[str(index)]["narration"]:
            found = True
        else:
            index += 1

    return index if found else 0
        

def get_times_between_turns(playthrough: dict):
    number_of_turns = get_turns_to_complete_objective (playthrough)

    deltas = []
    for i in range(0,number_of_turns):
        deltas += [time.mktime(time.strptime((playthrough[str(i+1)]["date"]))) - time.mktime(time.strptime((playthrough[str(i)]["date"])))]

    return deltas 

def statistic_summary (values: list):
    summary = {
        "min": numpy.min(values),
        "max": numpy.max(values),
        "mean": numpy.mean(values)
    }
    
    return summary


def get_narrations_length(playthrough: dict, include_starting_narration: bool = True):
    number_of_turns = get_turns_to_complete_objective(playthrough)
    narrations_length = []

    if include_starting_narration:
        narrations_length = [len(playthrough["0"]["starting_narration"])]

    for i in range(1,number_of_turns+1):
        narrations_length += [len(playthrough[str(i)]["narration"])]

    return narrations_length

def generate_txt_from_playthrough(playthrough):
    number_of_turns = get_turns_to_complete_objective(playthrough)
    turns_text = ""

    turns_text+= f'\n======= TURN 1 ======='
    turns_text+= f'\n\n🌐 World state 🌐\n{playthrough["0"]["initial_rendered_world_state"]}'
    turns_text+= f'\n\n📖 Automated GM 📖\n"{playthrough["0"]["starting_narration"].replace("\n","")}"'
    turns_text+= f'\n\n👉 Player utterance 👈\n"{playthrough["1"]["user_input"]}"'   
    turns_text+= f'\n\n⚙️ Predicted transformations ⚙️\n{playthrough["1"]["predicted_outcomes"]}'

    for turn in range(2,number_of_turns+1):
        turns_text+= f'\n======= TURN {str(turn)} ======='
        turns_text+= f'\n\n🌐 World state 🌐\n{playthrough[str(turn)]["previous_rendered_world_state"]}'
        turns_text+= f'\n\n📖 Automated GM 📖\n"{playthrough[str(turn-1)]["narration"].replace("\n","")}"'
        turns_text+= f'\n\n👉 Player utterance 👈\n"{playthrough[str(turn)]["user_input"]}"'
        turns_text+= f'\n\n⚙️ Predicted transformations ⚙️\n{playthrough[str(turn)]["predicted_outcomes"]}'
    
    turns_text+= f'\n======= TURN {str(number_of_turns+1)} ======='
    turns_text+= f'\n\n🌐 World state 🌐\n{playthrough[str(number_of_turns)]["updated_rendered_world_state"]}'
    turns_text+= f'\n\n📖 Automated GM 📖\n"{playthrough[str(number_of_turns)]["narration"].replace("\n","")}"'

        

    text = f"📄 Original file: '{playthrough_filename}'\n\n"
    text += f"🙋‍♀️ Player: {playthrough["nickname"]}\n"
    text += f"🖼️ Scenario: {playthrough["world_id"]}\n"
    text += f"#️⃣ Number of turns to complete the scenario: {str(number_of_turns)}\n"
    text += f"⏰ Elapsed time : {time.localtime(get_elapsed_time("0",str(number_of_turns), playthrough)).tm_min} minutes and {time.localtime(get_elapsed_time("0",str(number_of_turns), playthrough)).tm_sec} seconds\n"
    text += f"\t⏰ Elapsed time since the player sent the first message: {time.localtime(get_elapsed_time("1",str(number_of_turns), playthrough)).tm_min} minutes and {time.localtime(get_elapsed_time("0",str(number_of_turns), playthrough)).tm_sec} seconds\n"
    text += f"\t⏰ Shortest turn: {"{:.2f}".format(statistic_summary(get_times_between_turns(playthrough))["min"])} seconds\n"
    text += f"\t⏰ Average turn: {"{:.2f}".format(statistic_summary(get_times_between_turns(playthrough))["mean"])} seconds\n"
    text += f"\t⏰ Longest turn: {"{:.2f}".format(statistic_summary(get_times_between_turns(playthrough))["max"])} seconds\n"
    text += turns_text
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text



if __name__ == "__main__":

    ignored_playthroughs = ignored_playthroughs_list(os.path.join(PATH_PLAYTHROUGHS,"raw",'do_not_process_these_playthroughs.txt'))

    for playthrough_filename in os.listdir(os.path.join(PATH_PLAYTHROUGHS, "raw")):
        if playthrough_filename.endswith(".json") and playthrough_filename not in ignored_playthroughs:
            with open(os.path.join(PATH_PLAYTHROUGHS,"raw", playthrough_filename), 'r', encoding='utf-8') as f:
                playthrough = json.load(f)

            if get_turns_to_complete_objective(playthrough)==0:
                print(f"Error (file '{playthrough_filename}'): This script only processes complete playthroughs.")
            else:
                playthrough_as_text = generate_txt_from_playthrough(playthrough)

                with open (os.path.join(PATH_PLAYTHROUGHS, playthrough_filename[:-5] + '.txt'), 'w', encoding='utf-8') as f:
                    f.write(playthrough_as_text)
                    print(f"{playthrough_filename} ({playthrough["nickname"]}) ...done")