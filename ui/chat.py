# ui/chat.py

import os
from urllib.parse import urlparse

import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000/assistant")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("ASSISTANT_REQUEST_TIMEOUT_SECONDS", "180"))
UI_AUTO_REFRESH_SECONDS = int(os.getenv("UI_AUTO_REFRESH_SECONDS", "10"))


def _backend_base_url():
    parsed = urlparse(API_URL)
    return f"{parsed.scheme}://{parsed.netloc}"


BACKEND_BASE_URL = _backend_base_url()
AUTONOMY_STATUS_URL = f"{BACKEND_BASE_URL}/autonomy/status"
AUTONOMY_JOBS_URL = f"{BACKEND_BASE_URL}/autonomy/jobs"
AUTONOMY_CHECKPOINTS_URL = f"{BACKEND_BASE_URL}/autonomy/checkpoints"
AUTONOMY_RUN_ONCE_URL = f"{BACKEND_BASE_URL}/autonomy/run-once"
TRAINING_TOPICS_URL = f"{BACKEND_BASE_URL}/training/topics"


def _fetch_json(url: str):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json(), None
    except requests.Timeout:
        return None, "Timed out while waiting for the Dell backend."
    except requests.RequestException as exc:
        return None, f"Request error: {exc}"
    except ValueError:
        return None, "The backend returned invalid JSON."


def _post_json(url: str):
    try:
        response = requests.post(url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json(), None
    except requests.Timeout:
        return None, "Timed out while waiting for the Dell backend."
    except requests.RequestException as exc:
        return None, f"Request error: {exc}"
    except ValueError:
        return None, "The backend returned invalid JSON."


def _summarize_jobs(payload: dict):
    jobs = payload.get("jobs", [])[:5]
    if not jobs:
        return "No autonomy jobs yet."

    lines = []
    for job in jobs:
        lines.append(
            f"- `{job.get('type', 'unknown')}` | `{job.get('status', 'unknown')}` | source=`{job.get('source', 'unknown')}`"
        )
    return "\n".join(lines)


def _summarize_checkpoints(payload: dict):
    promoted = payload.get("promoted")
    items = payload.get("items", [])

    if promoted:
        promoted_line = f"Promoted checkpoint: `{promoted.get('id', 'unknown')}` with score `{promoted.get('benchmark', {}).get('score', 'n/a')}`"
    else:
        promoted_line = "No promoted checkpoint yet."

    if not items:
        return promoted_line

    latest = items[-3:]
    lines = [promoted_line, ""]
    for item in latest:
        lines.append(
            f"- `{item.get('id', 'unknown')}` | `{item.get('status', 'unknown')}` | score=`{item.get('benchmark', {}).get('score', 'n/a')}`"
        )
    return "\n".join(lines)


def _render_autonomy_panel():
    status_payload, status_error = _fetch_json(AUTONOMY_STATUS_URL)
    jobs_payload, jobs_error = _fetch_json(AUTONOMY_JOBS_URL)
    checkpoints_payload, checkpoints_error = _fetch_json(AUTONOMY_CHECKPOINTS_URL)

    st.subheader("ForgeMind Autonomy")
    st.caption(f"Dell backend: `{BACKEND_BASE_URL}`")

    col1, col2, col3, col4 = st.columns(4)

    if status_payload:
        queue = status_payload.get("queue", {})
        with col1:
            st.metric("Worker", "Running" if status_payload.get("running") else "Stopped")
        with col2:
            st.metric("Queue", queue.get("total", 0))
        with col3:
            st.metric("Completed", queue.get("completed", 0))
        with col4:
            st.metric("Checkpoints", status_payload.get("checkpoints", 0))
    else:
        with col1:
            st.metric("Worker", "Unavailable")
        with col2:
            st.metric("Queue", "-")
        with col3:
            st.metric("Completed", "-")
        with col4:
            st.metric("Checkpoints", "-")

    if status_error:
        st.error(status_error)
    elif status_payload:
        st.info(
            f"Auto-start=`{status_payload.get('auto_start')}` | Poll seconds=`{status_payload.get('poll_seconds')}` | "
            f"Last cycle=`{status_payload.get('last_cycle_at') or 'not yet'}`"
        )
        last_result = status_payload.get("last_result", {})
        if last_result:
            st.markdown("**Latest autonomy result**")
            st.json(last_result)

    left, right = st.columns(2)

    with left:
        st.markdown("**Job activity**")
        if jobs_error:
            st.error(jobs_error)
        elif jobs_payload:
            st.markdown(_summarize_jobs(jobs_payload))

    with right:
        st.markdown("**Checkpoint activity**")
        if checkpoints_error:
            st.error(checkpoints_error)
        elif checkpoints_payload:
            st.markdown(_summarize_checkpoints(checkpoints_payload))


def _render_training_panel():
    payload, error = _fetch_json(TRAINING_TOPICS_URL)

    st.subheader("Training Memory")
    if error:
        st.error(error)
        return

    summary = payload.get("summary", {})
    topics = payload.get("topics", [])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topics", summary.get("topics", 0))
    with col2:
        st.metric("Knowledge", summary.get("knowledge_items", 0))
    with col3:
        st.metric("Model Decisions", summary.get("model_decisions", 0))

    if not topics:
        st.caption("No topic-training runs recorded yet.")
        return

    latest = topics[:5]
    for topic in latest:
        st.markdown(
            f"**{topic.get('topic', 'unknown')}** | status=`{topic.get('status', 'unknown')}` | "
            f"knowledge=`{topic.get('knowledge_count', 0)}`"
        )
        st.caption(
            f"Completed subtopics: {', '.join(topic.get('completed_subtopics', [])) or 'none yet'}"
        )


st.set_page_config(page_title="ForgeMind", layout="wide")

st.title("ForgeMind")
st.caption("Chat from Streamlit, runtime and autonomy from the Dell server.")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

with st.sidebar:
    st.header("Runtime")
    st.write(f"Assistant URL: `{API_URL}`")
    st.write(f"Backend URL: `{BACKEND_BASE_URL}`")

    st.session_state.auto_refresh = st.toggle("Auto refresh", value=st.session_state.auto_refresh)

    if st.button("Run autonomy cycle now", use_container_width=True):
        payload, error = _post_json(AUTONOMY_RUN_ONCE_URL)
        if error:
            st.error(error)
        else:
            st.success("Autonomy cycle triggered.")
            st.json(payload)

if st.session_state.auto_refresh:
    components.html(
        f"""
        <script>
        setTimeout(function() {{
            window.parent.location.reload();
        }}, {UI_AUTO_REFRESH_SECONDS * 1000});
        </script>
        """,
        height=0,
    )

_render_autonomy_panel()
st.divider()
_render_training_panel()

st.divider()
st.subheader("Chat")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Type your message...")

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
        result = "The assistant timed out while waiting for the Dell model server."
    except requests.RequestException as exc:
        result = f"Request error: {exc}"
    except ValueError:
        result = "The server returned an invalid response."

    with st.chat_message("assistant"):
        st.markdown(result)

    st.session_state.messages.append({"role": "assistant", "content": result})
