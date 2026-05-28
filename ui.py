import gradio as gr
from utils.config_loader import load_config


def create_and_launch_interface(game_loop_fn, starting_narration):
    """Create and launch the Gradio interface for PAYADOR.
    
    Args:
        game_loop_fn: Reference to the game_loop function from app.py
        starting_narration: Initial scene narration to display
    
    Returns:
        The Gradio Blocks interface object
    """
    
    # Load configuration for debug info setting
    config_data = load_config()
    show_debug_info = config_data['config'].getboolean('UI', 'ShowDebugInfo', fallback=False)
    
    # Wrapper function for Gradio interface with multiple outputs
    def chat_with_display(message, history):
        # References globals: last_predicted_outcomes, last_world_state (set by game_loop)
        agent_response = game_loop_fn(message, history)
        
        # Import here to access module-level globals from parent
        import sys
        app_module = sys.modules.get('__main__')
        last_predicted = getattr(app_module, 'last_predicted_outcomes', '')
        last_world = getattr(app_module, 'last_world_state', '')
        
        return agent_response, last_predicted, last_world
    
    # Instantiate the Gradio app with custom layout
    with gr.Blocks(title="PAYADOR") as gradio_interface:
        gr.Markdown("# PAYADOR")
        gr.Markdown("[https://github.com/pln-fing-udelar/payador](https://github.com/pln-fing-udelar/payador)")
        
        # Hidden state to store the message while processing
        message_state = gr.State(value="")
        
        with gr.Row():
            with gr.Column(scale=2 if show_debug_info else 1):
                chatbot = gr.Chatbot(
                    height=500,
                    value=[{"role": "assistant", "content": starting_narration.replace("<", r"\<").replace(">", r"\>")}],
                    label="Story"
                )
                
            with gr.Column(scale=1, visible=show_debug_info):
                predicted_outcomes_display = gr.Textbox(
                    label="🛠️ Transformation Predictions 🛠️",
                    interactive=False,
                    lines=10
                )
                world_state_display = gr.Textbox(
                    label="🌎 Current Symbolic World State 🌎 ",
                    interactive=False,
                    lines=10
                )
        
        textbox = gr.Textbox(
            placeholder="What do you want to do?",
            label="Your Action",
            container=True
        )
        
        # Handle chat submission
        def add_user_message(message, chat_history):
            """Add the user message to chat history immediately for visual feedback."""
            if not message or message.strip() == "":
                return chat_history
            chat_history.append({"role": "user", "content": message})
            return chat_history
        
        def process_input(message, chat_history):
            if not message or message.strip() == "":
                return chat_history, "", ""
            
            # Call the game loop and get responses
            agent_response, predicted, world_state = chat_with_display(message, chat_history)
            
            # Add only the assistant response (user message already added)
            chat_history.append({"role": "assistant", "content": agent_response})
            
            return chat_history, predicted, world_state
        
        # Submit button triggers the processing
        submit_button = gr.Button("Send", variant="primary")
        
        # Event chain: save message -> add user to chat -> clear textbox -> process LLM
        submit_button.click(
            fn=lambda msg: msg,
            inputs=[textbox],
            outputs=[message_state]
        ).then(
            fn=add_user_message,
            inputs=[message_state, chatbot],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[textbox],
            queue=False
        ).then(
            fn=process_input,
            inputs=[message_state, chatbot],
            outputs=[chatbot, predicted_outcomes_display, world_state_display]
        )
        
        # Allow Enter key to submit (same chain as button)
        textbox.submit(
            fn=lambda msg: msg,
            inputs=[textbox],
            outputs=[message_state]
        ).then(
            fn=add_user_message,
            inputs=[message_state, chatbot],
            outputs=[chatbot]
        ).then(
            fn=lambda: "",
            outputs=[textbox],
            queue=False
        ).then(
            fn=process_input,
            inputs=[message_state, chatbot],
            outputs=[chatbot, predicted_outcomes_display, world_state_display]
        )
    
    return gradio_interface
