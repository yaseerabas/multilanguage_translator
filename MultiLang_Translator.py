import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(
    page_title="Language Translator",
    layout="centered",
    initial_sidebar_state="expanded",
)

LANGUAGES = {
    "Auto-Detect": "auto",
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Italian": "Italian",
    "Portuguese": "Portuguese",
    "Dutch": "Dutch",
    "Russian": "Russian",
    "Chinese (Simplified)": "Chinese (Simplified)",
    "Japanese": "Japanese",
    "Korean": "Korean",
    "Arabic": "Arabic",
    "Hindi": "Hindi",
    "Bengali": "Bengali",
    "Urdu": "Urdu",
    "Turkish": "Turkish",
    "Vietnamese": "Vietnamese",
    "Polish": "Polish",
    "Swedish": "Swedish",
    "Norwegian": "Norwegian",
    "Danish": "Danish",
    "Finnish": "Finnish",
    "Greek": "Greek",
    "Hebrew": "Hebrew",
    "Thai": "Thai",
    "Indonesian": "Indonesian",
    "Malay": "Malay",
    "Swahili": "Swahili",
}

def configure_gemini_api(api_key):
    """Configures the Gemini API with the provided key."""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Failed to configure API: {e}")
        return False

def initialize_gemini_model(model_name="gemini-1.5-flash-latest"):
    """Initializes the Gemini generative model."""
    try:
        return genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"Error initializing Gemini model: {e}")
        return None

def translate_text_with_gemini(model, text_to_translate, source_lang, target_lang):
    """
    Translates text using the Gemini API.
    """
    if not text_to_translate.strip():
        return "Please enter some text to translate."

    if source_lang == "auto":
        prompt = f"Detect the language of the following text and then translate it to {target_lang}: \"{text_to_translate}\". Provide only the translated text."
    else:
        prompt = f"Translate the following text from {source_lang} to {target_lang}: \"{text_to_translate}\". Provide only the translated text."

    try:
        response = model.generate_content(prompt)
        if response.parts:
            translated_text = response.parts[0].text
        else: 
            translated_text = response.text if hasattr(response, 'text') else "Could not extract translation."


        return translated_text
    except genai.types.generation_types.BlockedPromptException as e:
        return f"⚠️ Your request was blocked. Reason: {e}"
    except Exception as e:
        st.error(f"Translation error: {e}")
        return "An error occurred during translation."


with st.sidebar:
    st.header("🔑 API Configuration")
    st.markdown("""
        Enter your Google API Key.
        Get yours from [Google AI Studio](https://aistudio.google.com/app/apikey).
    """)

    api_key_from_secrets = st.secrets.get("GEMINI_API_KEY")
    if api_key_from_secrets:
        st.success("API Key loaded from secrets!", icon="✅")
        gemini_api_key = api_key_from_secrets
    else:
        gemini_api_key = st.text_input("Enter your Gemini API Key:", type="password", key="translator_api_key_input")

    if gemini_api_key:
        if configure_gemini_api(gemini_api_key):
            st.session_state.translator_api_configured = True
            if "translator_model" not in st.session_state or st.session_state.translator_model is None:
                st.session_state.translator_model = initialize_gemini_model()

            if st.session_state.get("translator_api_configured") and st.session_state.get("translator_model"):
                 st.success("API Configured & Model Loaded!", icon="🚀")
            else:
                st.error("Failed to initialize model. Check API key and console for errors.")
        else:
            st.session_state.translator_api_configured = False
            st.error("Invalid API Key or configuration error.")
    else:
        st.warning("Please enter your API Key.")
        st.session_state.translator_api_configured = False

st.title("Language Translator")
st.caption("Translate text into various languages.")

if not st.session_state.get("translator_api_configured") or not st.session_state.get("translator_model"):
    st.info("Please configure your API Key in the sidebar to use the translator.")
else:
    col1, col2 = st.columns(2)
    with col1:
        source_language_label = st.selectbox(
            "Source Language:",
            options=list(LANGUAGES.keys()),
            index=0,  # Default to 'Auto-Detect'
            key="source_lang_selector"
        )
        source_language_code = LANGUAGES[source_language_label]

    with col2:
        # Filter out "Auto-Detect" for target languages
        target_language_options = {k: v for k, v in LANGUAGES.items() if k != "Auto-Detect"}
        target_language_label = st.selectbox(
            "Target Language:",
            options=list(target_language_options.keys()),
            index=0,  # Default to 'English' if 'Auto-Detect' was 0
            key="target_lang_selector"
        )
        target_language_code = target_language_options[target_language_label]


    text_to_translate = st.text_area("Enter text to translate:", height=150, key="text_input_area")

    if st.button("Translate", key="translate_button"):
        if text_to_translate:
            with st.spinner(f"Translating to {target_language_label}..."):
                model = st.session_state.translator_model
                # Simple prompt version:
                translated_text = translate_text_with_gemini(
                    model,
                    text_to_translate,
                    source_language_code, # This would be the actual language name or 'auto'
                    target_language_label # Send the full name for clarity in the prompt
                )

                # If you implement parsing for detected language:
                # translated_text, detected_lang = translate_text_with_gemini(...)
                # if detected_lang:
                #     st.info(f"Detected source language: {detected_lang}")

                st.subheader("Translated Text:")
                st.markdown(f"> {translated_text}")
        else:
            st.warning("Please enter some text to translate.")