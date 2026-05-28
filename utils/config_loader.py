import configparser
import time
from models import get_llm


def load_config():
    """Load configuration from config.ini and initialize LLM models.
    
    Returns:
        dict: Configuration dictionary containing:
            - config: ConfigParser object
            - language: Game language setting
            - reasoning_model: Instantiated reasoning LLM
            - narrative_model: Instantiated narrative LLM
            - log_filename: Timestamped filename for game logs
            - reasoning_model_name: Name of the reasoning model
            - narrative_model_name: Name of the narrative model
    """
    # Read configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    # Language of the game
    language = config['Options']['SystemLanguage']
    
    # Model names from config
    reasoning_model_name = config['Models']['ReasoningModel']
    narrative_model_name = config['Models']['NarrativeModel']
    
    # Initialize the models
    reasoning_model = get_llm(reasoning_model_name)
    narrative_model = get_llm(narrative_model_name)
    
    # Create a name for the log file
    timestamp = time.time()
    today = time.gmtime(timestamp)
    log_filename = f"{today[0]}_{today[1]}_{today[2]}_{str(int(time.time()))[-5:]}.json"
    
    return {
        'config': config,
        'language': language,
        'reasoning_model': reasoning_model,
        'narrative_model': narrative_model,
        'log_filename': log_filename,
        'reasoning_model_name': reasoning_model_name,
        'narrative_model_name': narrative_model_name,
    }
