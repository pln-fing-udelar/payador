# PAYADOR
This repository contains the code for the PAYADOR approach, presented in the ICCC'24 paper “[PAYADOR: A Minimalist Approach to Grounding Language Models on Structured Data for Interactive Storytelling and Role-playing Games](https://computationalcreativity.net/iccc24/papers/ICCC24_paper_152.pdf)”.

TL;DR: The PAYADOR approach to the world-update problem in Interactive Storytelling consists of grounding Large Language Models to structured data to predict world-state transformations resulting from the player input.

Authors: [Santiago Góngora](https://scholar.google.com/citations?user=p1lKpmYAAAAJ), [Luis Chiruzzo](https://scholar.google.com/citations?user=C7c4uCsAAAAJ), [Gonzalo Méndez](https://scholar.google.com/citations?user=lC8QyOwAAAAJ) and [Pablo Gervás](https://scholar.google.com/citations?user=AcY-Y2gAAAAJ).


## 🗂️ Project structure
The PAYADOR approach is intended to be easily adaptable for other research problems in Interactive Storytelling. Here we will briefly describe each module.

### 🎮 Main Entry Point
**`app.py`** — Run this to start the PAYADOR system. It launches an interactive Gradio web interface where you can play and test the storytelling system.

### Core system modules 
- `ui.py` implements a Gradio-based web interface for interactive storytelling.
- `world.py` implements the world model (Items, Characters, Locations) and handles world state rendering and updates.
- `models.py` loads and prompts the Gemini model.
- `prompts.py` contains prompts for world-state transformation prediction and narrative generation.

### Utilities (`utils/`)
Infrastructure utilities and helper modules:
- `utils/config_loader.py` loads configuration settings from `config.ini` and initializes LLM models.
- `utils/world_serializer.py` handles JSON serialization and deserialization of world states.
- `utils/premade_worlds.py` provides utilities to load pre-configured worlds from JSON files.
- `utils/playthroughs_processing.py` provides utilities for analyzing and processing game playthroughs saved in JSON format.

### Admin & Maintenance Tools (`admin/`)
Optional utilities for managing the system:
- `admin/world_manager.py` — Standalone Flask API for CRUD operations on world scenarios (optional, not needed to play)
- `admin/world_manager.html` — Web interface for the World Manager tool

### Data Management (`data/`)
All data-related files and artifacts:
- `data/premade_worlds/` — Pre-configured world scenarios in JSON format (available in English and Spanish)
- `data/playthroughs/raw/` — Game playthroughs and logs from player sessions

## ⚙️ Usage

Please follow these steps to get this code running.

### Dependencies

To install the dependencies using [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html), just run

```shell
conda env create -f environment.yml
```

and then activate the environment


```shell
conda activate payador
```

### Configuration

The system uses a `config.ini` file to set some preferences. Here are the available configuration options:

**[Options]**
- `Language`: Game language (`es` for Spanish, `en` for English)
- `WorldID`: ID of the pre-made world to load (available worlds: 0-3)

**[UI]**
- `ShowDebugInfo`: Display the debug information panel with transformation predictions and world state (true/false)

**[Models]**
- `NarrativeModel`: LLM model used for narrative generation
- `ReasoningModel`: LLM model used for world-state transformation reasoning

### Gemini API key

The default implementation uses the Gemini API. Get [your API key](https://ai.google.dev/) and store it in a `.env` file (in the project root) with the appropriate environment variable name. The system will automatically load it.

...or modify `models.py` to use a different LLM! 

### Run PAYADOR!

Start PAYADOR by running:

```shell
python app.py
```

This launches a Gradio web interface where you can interact with the game. The system will load the pre-configured world specified in `config.ini` and await your input.

### Optional: World Manager Tool

To create or edit world scenarios, you can run the optional World Manager tool:

```shell
python admin/world_manager.py
```

This starts a Flask API on `http://localhost:5001` with a web interface for managing worlds. This is only needed if you want to create or modify game scenarios.

## 📄 Publications

This work is documented in two ICCC conference papers and the Master's thesis:

- **ICCC'24 Proceedings**: [PAYADOR: A Minimalist Approach to Grounding Language Models on Structured Data for Interactive Storytelling and Role-playing Games](https://computationalcreativity.net/iccc24/papers/ICCC24_paper_152.pdf)
- **ICCC'26 Proceedings**: [World-State Transformations for Neuro-symbolic Interactive Storytelling](https://arxiv.org/abs/2605.24719)
- **Master's Thesis**: [Approaches to interactive and improvisational storytelling](https://www.colibri.udelar.edu.uy/jspui/handle/20.500.12008/51156)

### Citation

If you use some part of this work in your research, please cite:

```
@inproceedings{gongora2024payador,
  title={PAYADOR: A Minimalist Approach to Grounding Language Models on Structured Data for Interactive Storytelling and Role-playing Games},
  author={G{\'o}ngora, Santiago and Chiruzzo, Luis and M{\'e}ndez, Gonzalo and Gerv{\'a}s, Pablo},
  booktitle={Proceedings of The 15th International Conference on Computational Creativity},
  year={2024}
}
```

```
@inproceedings{gongora2026transformations,
  title={World-State Transformations for Neuro-symbolic Interactive Storytelling},
  author={G{\'o}ngora, Santiago and Chiruzzo, Luis and M{\'e}ndez, Gonzalo and Gerv{\'a}s, Pablo},
  booktitle={Proceedings of The 17th International Conference on Computational Creativity},
  year={2026}
}
```
