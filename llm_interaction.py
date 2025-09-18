# llm_interaction.py
import config # To access GEMINI_MODEL and CONVERSATION_HISTORY
from tts_stt import speak # For speaking LLM responses

def get_gemini_response(user_input):
    """
    Sends user input to the Gemini model and processes the response.
    Manages conversation history using config.CONVERSATION_HISTORY.
    """
    # Append user input to conversation history
    config.CONVERSATION_HISTORY.append({"role": "user", "content": user_input})

    try:
        print("Sending command to Gemini Pro LLM...")

        # Prepare chat messages for Gemini
        gemini_chat_messages = []
        for msg in config.CONVERSATION_HISTORY:
            if msg["role"] == "user":
                gemini_chat_messages.append({'role': 'user', 'parts': [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_chat_messages.append({'role': 'model', 'parts': [msg["content"]]})
            elif msg["role"] == "system":
                # System messages are typically handled by defining the model's persona
                # For this specific structure, we'll treat it as a user prompt for the model
                gemini_chat_messages.append({'role': 'user', 'parts': [msg["content"]]})


        response = config.GEMINI_MODEL.generate_content(
            gemini_chat_messages,
            generation_config=config.genai.types.GenerationConfig( # Access genai from config
                max_output_tokens=150,
                temperature=0.7
            )
        )

        llm_response = response.text
        print(f"LLM Response: {llm_response}")
        speak(llm_response)

        # Append assistant's response to conversation history
        config.CONVERSATION_HISTORY.append({"role": "assistant", "content": llm_response})

    except Exception as e:
        speak("I am unable to process that request with my AI model at this moment. An anomaly has occurred.")
        print(f"Gemini LLM Error: {e}")
        # If an error occurs, remove the last user message to avoid polluting history
        if config.CONVERSATION_HISTORY and config.CONVERSATION_HISTORY[-1]["role"] == "user":
            config.CONVERSATION_HISTORY.pop()