# ui/chat.py

import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000/assistant"


st.set_page_config(page_title="AI Assistant", layout="wide")

st.title("🤖 Local AI Assistant")

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

uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"])

# -----------------------------
# HANDLE INPUT
# -----------------------------
if user_input or uploaded_file:

    # Show user message
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

    # Convert image to base64 if exists
    image_base64 = None
    if uploaded_file:
        image_bytes = uploaded_file.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        with st.chat_message("user"):
            st.image(uploaded_file, caption="Uploaded Image")

    # -----------------------------
    # API CALL
    # -----------------------------
    payload = {
        "message": user_input,
        "image": image_base64
    }

    try:
        response = requests.post(API_URL, json=payload)
        result = response.json().get("response", "No response")

    except Exception as e:
        result = f"Error: {e}"

    # -----------------------------
    # SHOW RESPONSE
    # -----------------------------
    with st.chat_message("assistant"):
        st.markdown(result)

    st.session_state.messages.append({"role": "assistant", "content": result})