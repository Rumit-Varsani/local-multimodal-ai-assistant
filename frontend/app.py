import streamlit as st
import requests

# ⚠️ CHANGE THIS when using from Mac
API_URL = "http://localhost:8000/assistant"

st.set_page_config(page_title="Local AI Assistant", layout="wide")

st.title("🧠 Local Multimodal AI Assistant")

if "chat" not in st.session_state:
    st.session_state.chat = []

user_input = st.text_input("Ask something:")

if st.button("Send") and user_input:
    try:
        response = requests.post(API_URL, params={"prompt": user_input})
        result = response.json()

        st.session_state.chat.append(("You", user_input))
        st.session_state.chat.append(("AI", result))

    except Exception as e:
        st.error(f"Error: {e}")

# Display chat history
for sender, message in st.session_state.chat:
    if sender == "You":
        st.markdown(f"**🧑 You:** {message}")
    else:
        st.markdown(f"**🤖 AI:** {message}")