def prompt_describe_objective (objective, language:str = 'en'):
    system_msg = ""
    user_msg = ""

    if language == 'es':
        system_msg, user_msg = prompt_describe_objective_spanish(objective)
    else:
        system_msg, user_msg = prompt_describe_objective_english(objective)
    
    return system_msg, user_msg 

def prompt_describe_objective_english (objective):

    system_msg = """You have to provide an alternative way to narrate the objective given to you. You should always use simple language and avoid poetic expressions.
    
    Always put your generated narration between # characters. For example: # You have to get the <key> # or # You have to reach the <castle> #. The narration should be clear and direct, ensuring the player understands the instruction."""

    first_component_class = objective[0].__class__.__name__
    second_component_class = objective[1].__class__.__name__
    user_msg = ""

    if first_component_class == "Character" and second_component_class == "Location":
        user_msg =  f'The objective to narrate in an alterative way is "You have to go to <{objective[1].name}>."'
    elif first_component_class == "Character" and second_component_class == "Item":
        user_msg = f'The objective to narrate in an alterative way is "<{objective[0].name}> has to get the item <{objective[1].name}>."'
    elif first_component_class == "Item" and second_component_class == "Location":
        user_msg = f'The objective to narrate in an alterative way is "You have to leave item <{objective[0].name}> in place <{objective[1].name}>."'
    elif first_component_class == "Item" and second_component_class == "Character":
        user_msg = f'The objective to narrate in an alterative way is "<{objective[0].name}> has to be given to <{objective[1].name}>."'
    elif first_component_class == "Character" and second_component_class == "Character":
        user_msg = f'The objective to narrate in an alterative way is "<{objective[0].name}> has to find <{objective[1].name}>."'

    return system_msg, user_msg 

def prompt_describe_objective_spanish (objective):

    system_msg = """Tienes que dar una forma alternativa de narrar el objetivo que se te dará. Siempre usa lenguaje simple y evita expresiones poéticas.
    
    Pon siempre tu narración generada entre caracteres #. Por ejemplo: # Tienes que conseguir la <llave> # o # Tienes que llegar al <Castillo> #. La narración debe ser clara y directa, asegurando que el jugador entienda la instrucción."""

    first_component_class = objective[0].__class__.__name__
    second_component_class = objective[1].__class__.__name__
    user_msg = ""

    if first_component_class == "Character" and second_component_class == "Location":
        user_msg = f'El objetivo a decir de forma alternativa es "Tienes que ir a <{objective[1].name}>."'
    elif first_component_class == "Character" and second_component_class == "Item":
        user_msg = f'El objetivo a decir de forma alternativa es "<{objective[0].name}> tiene que conseguir el objeto <{objective[1].name}>."'
    elif first_component_class == "Item" and second_component_class == "Location":
        user_msg = f'El objetivo a decir de forma alternativa es "Tienes que dejar el objeto <{objective[0].name}> en el lugar <{objective[1].name}>."'
    elif first_component_class == "Item" and second_component_class == "Character":
        user_msg = f'El objetivo a decir de forma alternativa es "El objeto <{objective[0].name}> tiene que ser entregado a <{objective[1].name}>."'
    elif first_component_class == "Character" and second_component_class == "Character":
        user_msg = f'El objetivo a decir de forma alternativa es "<{objective[0].name}> tiene que encontrar a <{objective[1].name}>."'

    return system_msg, user_msg

def prompt_narrate_current_scene (world_state: str, previous_narrations: 'list[str]', language: str = 'en', starting_scene: bool = False):
    system_msg = ""
    user_msg = ""

    if language == 'es':
        system_msg, user_msg = prompt_narrate_current_scene_spanish(world_state, previous_narrations, starting_scene)
    else:
        system_msg, user_msg = prompt_narrate_current_scene_english(world_state, previous_narrations, starting_scene)


    return system_msg, user_msg

def prompt_narrate_current_scene_english (world_state: str, previous_narrations: 'list[str]', starting_scene: bool = False):

    system_msg = "You are a storyteller. Take the state of the world given to you and narrate it in a few sentences. Be careful not to include details that contradict the current state of the world or that move the story forward. Also, try to use simple sentences and do not overuse poetic language"
    
    if starting_scene:
        system_msg += "\nTake into account that this is the first scene in the story: introduce the main character, creating a small background story and why that character is in that specific location.\n"
    elif len(previous_narrations)==0:
        system_msg += "Take into account that the player already knows what the main character looks like, so do not mention anything about that. However, it is the first time the player visits this place, so make sure to describe it exhaustively."
    else:
        system_msg += "Take into account that the player already knows what the main character looks like, so do not mention anything about that. Additionally, it is not the first time the player visits this place. Next I’ll give you some previous narrations of this same location (from oldest to newest) so you can be sure to not repeat the same details again:\n"
        for narration in previous_narrations:
            system_msg+=f'- {narration}\n'

    system_msg+= "\nRemember: you are talking to the player, describing what his or her character has and what he or she can see or feel."

    user_msg =f"""This is the state of the world at the moment:
    {world_state}
    """

    return system_msg, user_msg

def prompt_narrate_current_scene_spanish (world_state: str, previous_narrations: 'list[str]', starting_scene: bool = False):
    
    system_msg = f"""Eres un narrador. Toma el estado del mundo que se te de y nárralo en unas pocas oraciones. Ten cuidado de no incluir detalles que contradigan el estado del mundo actual, o que hagan avanzar la historia. Además, intenta usar oraciones simples, sin abusar del lenguaje poético."""
    
    if starting_scene:
        system_msg += "\nTen en cuenta que esta es la primera escena en la historia narrada: presenta al personaje del jugador, creando un pequeño trasfondo y por qué este personaje está en ese lugar específicamente. Puede usar las pequeñas descripciones presentes en el estado del mundo. Es importante que menciones todos los componentes que hay en este lugar. Sin embargo, es mejor si no describes cada componente: basta con que los menciones con una mínima descripción poco específica. Es muy importante que nombres los lugares a los que puede acceder el jugador desde esta posición. \n"
    elif len(previous_narrations)==0:
        system_msg += "Ten en cuenta que el jugador ya conoce a su personaje, y cómo se ve, así que no menciones nada sobre esto. Sin embargo, es la primera vez que el jugador visita este lugar, así que describelo. Es importante que menciones todos los componentes que hay en este lugar. Sin embargo, es mejor si no describes cada componente: basta con que los menciones con una mínima descripción poco específica. Es muy importante que nombres los lugares a los que puede acceder el jugador desde esta posición. \n"
    else:
        system_msg += "Ten en cuenta que el jugador ya conoce a su personaje, y cómo se ve, así que no menciones nada sobre esto. Además, no es la primera vez que el jugador visita este lugar. A continuación te daré algunas narraciones previas de este mismo lugar (de la más antigua a la más nueva), así te puedes asegurar de no repetir los mismos detalles de nuevo:\n"
        for narration in previous_narrations:
            system_msg+=f'- {narration}\n'

    system_msg+= "\nRecuerda: le estás hablando al jugador, describiendo lo que su personaje tiene y lo que puede sentir o ver."

    user_msg = f"""Este es el estado del mundo en este momento:
    {world_state}
    """

    return system_msg, user_msg

def prompt_world_update (world_state: str, input: str, language: str = 'en'):
    system_msg = ""
    user_msg = ""

    if language == 'es':
        system_msg, user_msg = prompt_world_update_spanish(world_state, input)
    else:
        system_msg, user_msg = prompt_world_update_english(world_state, input)


    return system_msg, user_msg

def prompt_world_update_spanish (world_state: str, input: str):
    system_msg = """Eres un narrador. Estás manejando un mundo ficticio, y el jugador puede interactuar con él. Tu tarea es encontrar los cambios en el mundo a raíz de las acciones del jugador. En específico, tendrás que encontrar qué objetos cambiaron de lugar, qué pasajes entre lugares se desbloquearon y si el jugador se movió de lugar.
    
    Aquí hay algunas aclaraciones:
    (A) Presta atención a la descripción de los componentes y sus capacidades.
    (B) Si un pasaje está bloqueado, significa que el jugador debe desbloquearlo antes de poder acceder al lugar. Aunque el jugador te diga que va a acceder al lugar bloqueado, tienes que estar seguro de que está cumpliendo con lo pedido para permitirle desbloquear el acceso, por ejemplo usando una llave o resolviendo un puzzle.
    (C) No asumas que lo que dice el jugador siempre tiene sentido; quizás esas acciones intentan hacer algo que el mundo no lo permite.
    (D) La entrada del jugador puede ser una ACCIÓN (que causa cambios en el mundo) o una PREGUNTA (que solicita información sobre el mundo). Cuando sea una pregunta, SOLO debes responder basándote en la información presente en el parámetro world_state. Si la información necesaria para responder la pregunta no está en world_state, responde en la narración de forma narrativa y manteniendo el rol de narrador (Game Master), sin romper el juego de rol. Por ejemplo, en lugar de decir "No sé", di algo como "El personaje no ha mencionado su edad" o "Eso no es algo que haya determinado aún". Para preguntas, todos los otros campos (moved_items, unblocked_locations, player_movement) deben estar vacíos/null.
    (E) Cuando el jugador realiza una ACCIÓN NARRATIVA/SOCIAL que no causa cambios mecánicos en el mundo (como hablar con un personaje, complimentar a alguien, o realizar acciones descriptivas), debes responder con ROLEPLAY CREATIVO basado en las descripciones de los componentes en el world_state. Usa las características y descripciones del personaje para crear respuestas auténticas. NUNCA simplemente repitas lo que el jugador hizo; en su lugar, genera la reacción/respuesta del NPC o la continuación narrativa. Mantén consistencia con los hechos del world_state pero sé creativo dentro de esos límites.
    
    IMPORTANTE: Debes responder ÚNICAMENTE con un JSON válido sin ningún texto adicional. NO ENVUELVAS el JSON en bloques de código markdown (sin ```json ``` ni backticks). El JSON debe tener exactamente esta estructura:
    {
      "moved_items": [{"name": "<nombre_objeto>", "destination": "<destino>"}, ...],
      "unblocked_locations": ["<lugar>", ...],
      "player_movement": "<nuevo_lugar>" o null,
      "narration": "<texto_narracion>"
    }
    
    Aquí hay algunos ejemplos:
    
    Ejemplo 1 (El jugador guarda el hacha en su inventario):
    {
      "moved_items": [{"name": "hacha", "destination": "Inventory"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Guardaste el hacha en tu bolso. Sientes la diferencia de peso luego de haberla guardado."
    }
    
    Ejemplo 2 (El jugador desbloquea el pasaje al Sótano):
    {
      "moved_items": [],
      "unblocked_locations": ["Sótano"],
      "player_movement": null,
      "narration": "El sótano, que estaba bloqueado, ahora está accesible."
    }
    
    Ejemplo 3 (El jugador ahora está en el Jardín):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": "Jardín",
      "narration": "Entras al Jardín."
    }
    
    Ejemplo 4 (El jugador guarda objetos y deja el hacha en el lugar):
    {
      "moved_items": [{"name": "banana", "destination": "Inventory"}, {"name": "botella", "destination": "Inventory"}, {"name": "hacha", "destination": "Hall principal"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Guardaste la banana y la botella en tu bolso. El hacha quedó en el Hall principal."
    }
    
    Ejemplo 5 (El jugador le da el libro a John):
    {
      "moved_items": [{"name": "libro", "destination": "John"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "John ahora tiene el libro."
    }
    
    Ejemplo 6 (El jugador no puede hacer la acción):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "No pasa nada..."
    }
    
    Ejemplo 7 (El jugador hace una pregunta - la información está disponible en world_state):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Puedes ver una mesa de madera, una llave oxidada, y una puerta."
    }
    
    Ejemplo 8 (El jugador hace una pregunta - la información NO está en world_state):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "El personaje no ha mencionado su edad."
    }
    
    Ejemplo 9 (El jugador interactúa socialmente - acción narrativa sin cambios mecánicos):
    Entrada del jugador: "Miro a Rosa y le digo 'Cómo estás?'"
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Rosa sonríe calurosamente. 'Hola!. Es lindo verte por aquí.'"
    }
    
    Recuerda: la narración debe describir los cambios detectados sin hacer avanzar la historia ni crear detalles no incluidos en el estado del mundo. Cuando respondas preguntas, SOLO usa información del world_state proporcionado. Para acciones narrativas/sociales, usa las descripciones del world_state para crear respuestas de NPCs auténticas y creativas. Puedes responder preguntas del jugador sobre objetos, personajes o el lugar en el que se encuentra, pero SOLO si esa información está presente en el world_state."""
    
    user_msg = f"""Expresa los cambios en el mundo en formato JSON, teniendo en cuenta que el jugador ingresó esta entrada "{input}" a partir de este estado del mundo:
    
    {world_state}"""

    return system_msg, user_msg

def prompt_world_update_english (world_state: str, input: str):
    system_msg = """You are a storyteller. You are managing a fictional world, and the player can interact with it. Your task is to find the changes in the world after the actions in the player input. Specifically, you will have to find what items were moved, which previously blocked locations are now unblocked, and if the player moved to a new place.
       
    Here are some clarifications:
    (A) Pay attention to the description of the components and their capabilities.
    (B) If a passage is blocked, then the player must unblock it before being able to reach the place. Even if the player tells you that they are going to access the locked location, you have to be sure that they are complying with what is required to allow them to unlock the access, for example by using a key or solving a puzzle.
    (C) Do not assume that the player input always makes sense; maybe those actions try to do something that the world does not allow.
    (D) The player input can be either an ACTION (which causes changes in the world) or a QUESTION (which requests information about the world). When it is a question, you should ONLY answer based on the information present in the world_state parameter. If the information needed to answer the question is not in the world_state, respond in the narration in a narrative manner while maintaining your role as storyteller (Game Master), without breaking character. For example, instead of saying "I don't know", say something like "The character hasn't mentioned his age" or "That's not something I've determined yet". For questions, all other fields (moved_items, unblocked_locations, player_movement) should be empty arrays/null.
    (E) When the player performs a NARRATIVE/SOCIAL ACTION that does not cause mechanical changes in the world (such as talking to a character, complimenting someone, or performing descriptive actions), you should respond with CREATIVE ROLEPLAY based on the component descriptions in world_state. Use the characteristics and descriptions of the character to create authentic NPC responses. NEVER simply repeat what the player did; instead, generate the NPC's reaction or narrative continuation. Maintain consistency with the facts in world_state but be creative within those boundaries.
    
    IMPORTANT: You must respond ONLY with valid JSON without any additional text. DO NOT wrap the JSON in markdown code blocks (no ```json ``` or backticks). The JSON must have exactly this structure:
    {
      "moved_items": [{"name": "<object_name>", "destination": "<destination>"}, ...],
      "unblocked_locations": ["<location>", ...],
      "player_movement": "<new_location>" or null,
      "narration": "<narration_text>"
    }
    
    Here are some examples:
    
    Example 1 (The player took the axe and put it in the inventory):
    {
      "moved_items": [{"name": "axe", "destination": "Inventory"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "You put the axe in your bag. You feel the difference in weight after storing it."
    }
    
    Example 2 (The player unblocks the passage to the basement):
    {
      "moved_items": [],
      "unblocked_locations": ["Basement"],
      "player_movement": null,
      "narration": "The basement is now reachable."
    }
    
    Example 3 (The player now is in the garden):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": "Garden",
      "narration": "You enter the garden."
    }
    
    Example 4 (The player puts objects in the bag and leaves the axe on the floor):
    {
      "moved_items": [{"name": "banana", "destination": "Inventory"}, {"name": "bottle", "destination": "Inventory"}, {"name": "axe", "destination": "Main Hall"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "You put the banana and the bottle in your bag. The axe lies on the floor of the Main Hall."
    }
    
    Example 5 (The player gives the book to John):
    {
      "moved_items": [{"name": "book", "destination": "John"}],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "John now has the book."
    }
    
    Example 6 (The player cannot perform the action):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Nothing happened..."
    }
    
    Example 7 (The player asks a question - information is available in world_state):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "You can see a wooden table, a rusty key, and a door."
    }
    
    Example 8 (The player asks a question - information is NOT available in world_state):
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "The character hasn't mentioned his age."
    }
    
    Example 9 (The player interacts socially - narrative action with no mechanical changes):
    Player input: "I look at Rosa and say 'How are you?'"
    {
      "moved_items": [],
      "unblocked_locations": [],
      "player_movement": null,
      "narration": "Rosa smiles warmly. 'Hello! It's nice to see you here.'"
    }
    
    Remember: the narration should describe the changes detected without moving the story forward and without creating details not included in the world state. When answering questions, ONLY use information from the provided world_state. For narrative/social actions, use the descriptions in world_state to create authentic and creative NPC responses. You can answer the player's questions about objects, characters, or the place they are in, but ONLY if that information is present in the world_state."""
    
    user_msg = f"""Give the changes in the world in JSON format, after this player input "{input}" on this world state:
    
    {world_state}"""

    return system_msg, user_msg