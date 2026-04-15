# PAYADOR
This repository contains the code for the PAYADOR approach, presented in the ICCC'24 paper “[PAYADOR: A Minimalist Approach to Grounding Language Models on Structured Data for Interactive Storytelling and Role-playing Games](https://computationalcreativity.net/iccc24/papers/ICCC24_paper_152.pdf)”.

TL;DR: The PAYADOR approach to the world-update problem in Interactive Storytelling (and Role-playing Games) consists of grounding Large Language Models to structured data to predict world-state transformations resulting from the player input.

Authors: [Santiago Góngora](https://scholar.google.com/citations?user=p1lKpmYAAAAJ), [Luis Chiruzzo](https://scholar.google.com/citations?user=C7c4uCsAAAAJ), [Gonzalo Méndez](https://scholar.google.com/citations?user=lC8QyOwAAAAJ) and [Pablo Gervás](https://scholar.google.com/citations?user=AcY-Y2gAAAAJ).


## 🗂️ Project structure
The PAYADOR approach is intended to be easily adaptable for other research problems in Interactive Storytelling. Here we will briefly describe each module and add comments about how they should be modified for other cases.

- `app.py` implements the main entry point and orchestrates the PAYADOR system.
- `ui.py` implements a Gradio-based web interface for interactive storytelling and role-playing gameplay.
- `world.py` implements the three components of the world model (Items, Characters and Locations) as well as the world itself. This module also implements the world state rendering in natural language and the update of the world state, key steps for the PAYADOR approach.
    - ❗ If you are working for a different language than English, you will need to adapt the *render_world* and *parse_updates* methods.
    - ❗ If you are working for other changes in the fictional world (e.g. mood during a conversation, like in the [Emolift paper](https://computationalcreativity.net/iccc2019/papers/iccc19-paper-44.pdf)) you will need to add another updates in the *parse_updates* method.
- `config_loader.py` loads configuration settings from `config.ini` and initializes the LLM models.
- `premade_worlds.py` includes simple ready-to-play worlds. Scenarios and world components are available in both English and Spanish.
- `world_serializer.py` handles JSON serialization and deserialization of world states.
- `playthroughs_processing.py` provides utilities for analyzing and processing game playthroughs saved in JSON format.
- `models.py` loads and prompts the Gemini model.
    - ❗ If you want to use a different model, you can add another class for it.
- `prompts.py` contains the prompts for world-state transformation prediction and narrative generation.
    - ❗ If you are working for a different language than English, you will need to adapt these prompts.
    - ❗ If you are working for other types of world-state transformations in the fictional world, you will need to update the *prompt_world_update* function.

## ⚙️ Usage

Please, follow these steps to get this code running.

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

The system uses a `config.ini` file to set the language and model names. You can adjust these settings as needed.

### Gemini API key

The default implementation uses the Gemini API. Get [your API key](https://ai.google.dev/) and store it in a `.env` file (in the project root) with the appropriate environment variable name. The system will automatically load it.

...or modify `models.py` to use a different LLM! 

### Run!

Finally, run `app.py`. This will launch a Gradio web interface where you can interact with the storytelling system.

```shell
python app.py
```

## 📄 Publications

This work is documented in the ICCC'24 conference paper and the Master's thesis:

- **ICCC'24 Proceedings**: [PAYADOR: A Minimalist Approach to Grounding Language Models on Structured Data for Interactive Storytelling and Role-playing Games](https://computationalcreativity.net/iccc24/papers/ICCC24_paper_152.pdf)
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
@mastersthesis{gongora2025approaches,
  title={Approaches to interactive and improvisational storytelling},
  author={G{\'o}ngora, Santiago},
  year={2025},
  school={Universidad de la Rep{\'u}blica, Facultad de Ingenier{\'i}a},
  url={https://hdl.handle.net/20.500.12008/51156}
}
```
