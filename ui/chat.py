# ui/chat.py

import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/assistant"
REQUEST_TIMEOUT_SECONDS = 60


st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("Local Text AI Assistant")
st.caption("Text-only mode with local memory and a local Ollama model.")

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# CHAT DISPLAY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------------
# INPUT AREA
# -----------------------------
user_input = st.chat_input("Type your message...")

# -----------------------------
# HANDLE INPUT
# -----------------------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    try:
        response = requests.post(
            API_URL,
            json={"message": user_input},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        result = response.json().get("response", "No response")
    except requests.Timeout:
        result = "The assistant timed out while waiting for the local model."
    except requests.RequestException as exc:
        result = f"Request error: {exc}"
    except ValueError:
        result = "The server returned an invalid response."

    with st.chat_message("assistant"):
        st.markdown(result)

    st.session_state.messages.append({"role": "assistant", "content": result})
