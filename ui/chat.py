import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.title("🧠 Rumit's Local AI Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

st.subheader("Upload Image")

uploaded_file = st.file_uploader("Choose an image", type=["png", "jpg", "jpeg"])

if uploaded_file:

    files = {"file": uploaded_file.getvalue()}

    response = requests.post(
        "http://127.0.0.1:8000/upload-image",
        files={"file": uploaded_file}
    )

    st.success("Image uploaded successfully!")

    st.image(uploaded_file)

# user input
prompt = st.chat_input("Ask something...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    response = requests.post(API_URL, params={"prompt": prompt})

    ai_reply = response.json()["response"]

    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

    with st.chat_message("assistant"):
        st.write(ai_reply)