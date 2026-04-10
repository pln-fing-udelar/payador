def prompt_describe_objective (objective, language:str = 'en'):
    system_msg = ""
    user_msg = ""

    if language == 'es':
        system_msg, user_msg = prompt_describe_objective_spanish(objective)
    else:
        system_msg, user_msg = prompt_describe_objective_english(objective)
    
    return system_msg, user_msg 

def prompt_describe_objective_english (objective):

    system_msg = """You have to provide an alternative way to narrate the objective given to you. You should always use simple language. 
    
    Always put your generated narration between # characters. For example: # You have to get the <key> # or # You have to reach the <castle> #. The narration may be poetic yet clear, ensuring the player understands the instruction."""

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

    system_msg = """Tienes que dar una forma alternativa de narrar el objetivo que se te dará. Siempre usa lenguaje simple. 
    
    Pon siempre tu narración generada entre caracteres #. Por ejemplo: # Tienes que conseguir la <llave> # o # Tienes que llegar al <Castillo> #. La narración puede ser poética pero clara, asegurando que el jugador entienda la instrucción."""

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
    system_msg = f"""Eres un narrador. Estás manejando un mundo ficticio, y el jugador puede interactuar con él. Siguiendo un formato específico, que voy a explicarte más abajo, tu tarea es encontrar los cambios en el mundo a raíz de las acciones del jugador. En específico, tendrás que encontrar qué objetos cambiaron de lugar, qué pasajes entre lugares se desbloquearon y si el jugador se movió de lugar.
    
    Aquí hay algunas aclaraciones:
    (A) Presta atención a a la descripción de los componentes y sus capacidades.
    (B) Si un pasaje está bloqueado, significa que el jugador debe desbloquearlo antes de poder acceder al lugar. Aunque el jugador te diga que va a acceder al lugar bloqueado, tienes que estar seguro de que está cumpliendo con lo pedido para permitirle desbloquear el acceso, por ejemplo usando una llave o resolviendo un puzzle.
	(C) No asumas que lo que dice el jugador siempre tiene sentido; quizás esas acciones intentan hacer algo que el mundo no lo permite.
    (D) Sigue siempre el siguiente formato con las tres categorías, usando "None" en cada caso si no hay cambios y repite la categoría por cada caso:
    - Moved object: <object> now is in <new_location>
    - Blocked passages now available: <now_reachable_location>
    - Your location changed: <new_location>
    (E) Por último, puedes agregar una narración de los cambios detecados en el estado del mundo (¡sin hacer avanzar la historia y sin crear detalles no incluidos en el estado del mundo!) usando el formato: #tu mensaje final#
    (F) Dentro de la sección de narración que agregues al final, entre símbolos #, también puedes responder preguntas que haga el jugador en su entrada, sobre los objetos o personajes que puede ver, o el lugar en el que se encuentra.

    Aquí hay algunos ejemplos (con la aclaración entre paréntesis sobre qué podría haber intentado hacer el jugador) sobre el formato, descritos en los puntos (D) y (E):
    
    Ejemplo 1 (El jugador guarda el hacha en su inventario)
    - Moved object: <hacha> now is in <Inventory>
    - Blocked passages now available: None
    - Your location changed: None
    # Guardaste el hacha en tu bolso. Sientes la diferencia de peso luego de haberla guardado #

    Ejemplo 2 (El jugador desbloquea el pasaje al Sótano)
    - Moved object: None
    - Blocked passages now available: <Sótano>
    - Your location changed: None
    # El sótano, que estaba bloqueado, ahora está accesible #

    Ejemplo 3 (El jugador ahora está en el Jardín)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed: <Jardín>
    # Entras al Jardín #

    Ejemplo 4 (El jugador guarda objetos y deja el hacha en el lugar)
    - Moved object: <banana> now is in <Inventory>,  <botella> now is in <Inventory>,  <hacha> now is in <Hall principal>
    - Blocked passages now available: None
    - Your location changed: None
    # Guardaste la banana y la botella en tu bolso. El hacha quedó en el Hall principal #

    Ejemplo 5 (El jugador guarda objetos, deja el hacha en el lugar y desbloquea el pasaje a la Pequeña habitación)
    - Moved object: <banana> now is in <Inventory>,  <botella> now is in <Inventory>,  <hacha> now is in <Hall principal>
    - Blocked passages now available: <Pequeña habitación>
    - Your location changed: None
    # Guardaste la banana y la botella en tu bolso. El hacha quedó en el Hall principal. Además, la pequeña habitación ahora está accesible. #

    Ejemplo 6 (El jugador guarda objetos, deja el hacha en el lugar, desbloquea el pasaje y se mueve a la Pequeña habitación)
    - Moved object: <banana> now is in <Inventory>,  <botella> now is in <Inventory>,  <hacha> now is in <Hall principal>
    - Blocked passages now available: <Pequeña habitación>
    - Your location changed:  <Pequeña habitación>
    # Guardaste la banana y la botella en tu bolso. El hacha quedó en el Hall principal. Además, la pequeña habitación ahora está accesible e ingresaste a ella #

    Ejemplo 7 (El jugador guarda el lápiz y le da un libro a John)
    - Moved object: <libro> now is in <John>,  <lápiz> now is in <Inventory>
    - Blocked passages now available: None
    - Your location changed:  None
    # John ahora tiene el libro. Tú guardaste el lápiz en tu bolso #

    Ejemplo 8 (El jugador le da la computadora a Susan)
    - Moved object: <computadora> now is in <Susan>
    - Blocked passages now available: None
    - Your location changed:  None
    # Susan guardó la computadora en su bolso #

    Ejemplo 9 (El jugador hace algo que no tiene como resultado el efecto que esperaba)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed:  None
    # No pasa nada... #

    Ejemplo 10 (El jugador hace una pregunta)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed:  None
    # Respuesta a la pregunta del jugador #"""
    
    
    user_msg = f"""Expresa los cambios en el mundo siguiendo el formato pedido, teniendo en cuenta que el jugador ingresó esta entrada "{input}" a partir de este estado del mundo:
    
    {world_state}"""

    return system_msg, user_msg

def prompt_world_update_english (world_state: str, input: str):
    system_msg = f"""You are a storyteller. You are managing a fictional world, and the player can interact with it. Following a specific format, that I will specify below, your task is to find the changes in the world after the actions in the player input. Specifically, you will have to find what objects were moved, which previously blocked passages are now unblocked, and if the player moved to a new place.
       
    Here are some clarifications:
    (A) Pay attention  to the description of the components and their capabilities.
    (B) If a passage is blocked, then the player must unblock it before being able to reach the place. Even if the player tells you that he is going to access the locked location, you have to be sure that he is complying with what you asked to allow him to unlock the access, for example by using a key or solving a puzzle.
    (C) Do not assume that the player input always makes sense; maybe those actions try to do something that the world does not allow.
    (D) Follow always the following format with the three categories, using "None" in each case if there are no changes and repeat the category for each case:
    - Moved object: <object> now is in <new_location>
    - Blocked passages now available: <now_reachable_location>
    - Your location changed: <new_location>
    (E) Finally, you can narrate the changes you've detected in the world state (without moving the story forward and without making up details not included in the world state!) using the format: #your final message#
    (F) In the narration section that you add at the end, between # symbols, you can also answer questions that the player asks in their input, about the objects or characters they can see, or the place they are in.

    Here I give you some examples (in parentheses, a clarification about what the player might have tried to do) for the asked format, as described in items (D) and (E):

    Example 1 (The player took the axe and put it in the inventory)
    - Moved object: <axe> now is in <Inventory>
    - Blocked passages now available: None
    - Your location changed: None
    #You put the axe in your bag#

    Example 2 (The player unblocks the passage to the basement)
    - Moved object: None
    - Blocked passages now available: <Basement>
    - Your location changed: None
    # The basement is now reachable #

    Example 3 (The player now is in the garden)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed: <Garden>
    # You enter the garden #

    Example 4 (The player puts objects in the bag and leaves the axe on the floor)
    - Moved object: <banana> now is in <Inventory>,  <bottle> now is in <Inventory>,  <axe> now is in <Main Hall>
    - Blocked passages now available: None
    - Your location changed: None
    # You put the banana and the bottle in your bag. The axe lies on the floor of the Main hall #

    Example 5 (The player puts objects in the bag and leaves the axe on the floor and unblocks the passage to the Small room)
    - Moved object: <banana> now is in <Inventory>,  <bottle> now is in <Inventory>,  <axe> now is in <Main Hall>
    - Blocked passages now available: <Small room>
    - Your location changed: None
    # You put the banana and the bottle in your bag. The axe lies on the floor of the Main hall. Now you can reach the Small room. #

    Example 6 (The player puts objects in the bag and leaves the axe on the floor, unblocks the passage and goes to the Small room)
    - Moved object: <banana> now is in <Inventory>,  <bottle> now is in <Inventory>,  <axe> now is in <Main Hall>
    - Blocked passages now available: <Small room>
    - Your location changed:  <Small room>
    # You put the banana and the bottle in your bag. The axe lies on the floor of the Main hall. The Small room is now unblocked, and you moved there. #

    Example 7 (The player puts the pencil in the bag and gives the book to John)
    - Moved object: <book> now is in <John>,  <pencil> now is in <Inventory>
    - Blocked passages now available: None
    - Your location changed:  None
    # John now has the book. You put the pencil in your bag #

    Example 8 (The player gives the computer to Susan)
    - Moved object: <computer> now is in <Susan>
    - Blocked passages now available: None
    - Your location changed:  None
    # Susan put the computer in her bag #

    Example 9 (The player does something that has not the expected outcome)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed:  None
    # Nothing happened... #

    Example 10 (The player asks a question)
    - Moved object: None
    - Blocked passages now available: None
    - Your location changed:  None
    # Answer to the player's question #"""
    
    
    user_msg = f"""Give the changes in the world following the specified format, after this player input "{input}" on this world state:
    
    {world_state}"""

    return system_msg, user_msg