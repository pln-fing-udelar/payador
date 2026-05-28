import json
import os
import time
import re
import numpy
from typing import Dict

PATH_PLAYTHROUGHS = 'data/playthroughs/'
DATE_FORMAT = "%a %b %d %H:%M:%S %Y"


def _parse_turn_timestamp(turn_key: str, playthrough: Dict) -> float:
    """Parse turn timestamp and return Unix timestamp.
    
    Args:
        turn_key: String key of the turn (e.g., "1", "2", "3")
        playthrough: Playthrough dictionary
        
    Returns:
        Unix timestamp as float
    """
    return time.mktime(time.strptime(playthrough[turn_key]["date"], DATE_FORMAT))

def get_elapsed_time(starting_turn: str, ending_turn: str, playthrough: dict) -> float:
    """Calculate elapsed time between two turns.
    
    Args:
        starting_turn: String key of starting turn (e.g., "1")
        ending_turn: String key of ending turn (e.g., "3")
        playthrough: Playthrough dictionary
        
    Returns:
        Elapsed time in seconds as float
    """
    starting_time = _parse_turn_timestamp(starting_turn, playthrough)
    ending_time = _parse_turn_timestamp(ending_turn, playthrough)
    return ending_time - starting_time

def get_turns_to_complete_objective(playthrough: dict) -> int:
    """Get the turn number in which the objective was completed.
    
    Args:
        playthrough: Playthrough dictionary
        
    Returns:
        Turn number (integer) when objective was completed
    """
    return playthrough["objective_completed_turn"]
        

def get_times_between_turns(playthrough: dict) -> list[float]:
    """Calculate time elapsed between consecutive turns.
    
    Args:
        playthrough: Playthrough dictionary
        
    Returns:
        List of elapsed times (in seconds) between consecutive turns
    """
    number_of_turns = get_turns_to_complete_objective(playthrough)
    deltas = []
    
    for i in range(1, number_of_turns):
        start_time = _parse_turn_timestamp(str(i), playthrough)
        end_time = _parse_turn_timestamp(str(i + 1), playthrough)
        deltas.append(end_time - start_time)

    return deltas 

def statistic_summary(values: list[float]) -> dict:
    """Calculate min, max, and mean statistics from values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with 'min', 'max', and 'mean' keys. Returns None values if list is empty.
    """
    if not values:
        return {
            "min": None,
            "max": None,
            "mean": None
        }
    
    return {
        "min": float(numpy.min(values)),
        "max": float(numpy.max(values)),
        "mean": float(numpy.mean(values))
    }


def get_narrations_length(playthrough: dict, include_starting_narration: bool = True) -> list[int]:
    """Get the length of narrations for each turn.
    
    Args:
        playthrough: Playthrough dictionary
        include_starting_narration: If True, include narration from turn 1 (starting scene)
        
    Returns:
        List of narration lengths (in characters) for each turn
    """
    number_of_turns = get_turns_to_complete_objective(playthrough)
    narrations_length = []

    # Turn 1 contains the starting narration
    if include_starting_narration:
        narrations_length.append(len(playthrough["1"]["narration"]))

    # Include narrations from subsequent turns
    for i in range(2, number_of_turns + 1):
        narrations_length.append(len(playthrough[str(i)]["narration"]))

    return narrations_length

def generate_txt_from_playthrough(playthrough: dict, playthrough_filename: str) -> str:
    """Generate a formatted text representation of a completed playthrough.
    
    Args:
        playthrough: Playthrough dictionary from JSON
        playthrough_filename: Original JSON filename for reference
        
    Returns:
        Formatted text string with turn-by-turn playthrough summary
    """
    # Discover all turns in the playthrough (numeric string keys)
    turn_keys = sorted([int(k) for k in playthrough.keys() if k.isdigit()])
    
    if not turn_keys:
        return "No turns found in playthrough."
    
    number_of_turns = max(turn_keys)
    turns_text = ""

    for turn in turn_keys:
        turns_text+= f'\n======= TURN {turn} ======='
        turns_text+= f'\n\n🌐 World state 🌐\n{playthrough[str(turn)]["previous_rendered_world_state"]}'
        turns_text+= f'\n\n📖 Automated GM 📖\n"{playthrough[str(turn)]["narration"].replace(chr(10), "")}"'
        turns_text+= f'\n\n👉 Player utterance 👈\n"{playthrough[str(turn)]["user_input"]}"'
        turns_text+= f'\n\n⚙️ Predicted transformations ⚙️\n' + (playthrough[str(turn)]["predicted_outcomes"] if isinstance(playthrough[str(turn)]["predicted_outcomes"], str) else json.dumps(playthrough[str(turn)]["predicted_outcomes"], indent=2))

    elapsed_total = get_elapsed_time("1", str(number_of_turns), playthrough)
    turn_times = get_times_between_turns(playthrough)
    stats = statistic_summary(turn_times)
    
    # Use objective_completed_turn if available for the summary, otherwise use max turn
    turns_to_complete = playthrough.get("objective_completed_turn", number_of_turns)

    text = f"📄 Original file: '{playthrough_filename}'\n\n"
    text += f"🙋‍♀️ Player: {playthrough['nickname']}\n"
    text += f"🖼️ Scenario: {playthrough['world_id']}\n"
    text += f"🌐 Language: {playthrough['language']}\n"
    text += f"#️⃣ Number of turns to complete the scenario: {turns_to_complete}\n"
    text += f"⏰ Elapsed time: {time.localtime(elapsed_total).tm_min} minutes and {time.localtime(elapsed_total).tm_sec} seconds\n"
    
    if stats['min'] is not None:
        text += f"\t⏰ Shortest turn: {stats['min']:.2f} seconds\n"
        text += f"\t⏰ Average turn: {stats['mean']:.2f} seconds\n"
        text += f"\t⏰ Longest turn: {stats['max']:.2f} seconds\n"
    
    text += turns_text
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text



if __name__ == "__main__":

    for playthrough_filename in os.listdir(os.path.join(PATH_PLAYTHROUGHS, "raw")):
        if playthrough_filename.endswith(".json"):
            with open(os.path.join(PATH_PLAYTHROUGHS,"raw", playthrough_filename), 'r', encoding='utf-8') as f:
                playthrough = json.load(f)

            # Only process playthroughs where the objective was actually completed
            if not playthrough.get("objective_completed", False):
                print(f"Skipping (file '{playthrough_filename}'): Objective was not completed.")
            else:
                playthrough_as_text = generate_txt_from_playthrough(playthrough, playthrough_filename)

                with open(os.path.join(PATH_PLAYTHROUGHS, playthrough_filename[:-5] + '.txt'), 'w', encoding='utf-8') as f:
                    f.write(playthrough_as_text)
                    print(f"{playthrough_filename} ({playthrough['nickname']}) ...done")
