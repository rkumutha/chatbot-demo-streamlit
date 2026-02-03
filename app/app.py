import os
import json
import requests
import streamlit as st

st.set_page_config(page_title="Chatbot Demo", page_icon="💬")

st.title("💬 Chatbot Demo")
st.caption("Demo UI (Streamlit) calling your REST API")

API_URL = os.getenv("API_URL", "").strip()
API_KEY = os.getenv("API_KEY", "").strip()  # optional

with st.sidebar:
    st.header("Settings")
    api_url_ui = st.text_input("API URL", value=API_URL, placeholder="https://your-api.com/chat")
    st.markdown("If your API needs a key, set it as a Streamlit Secret (recommended).")
    timeout_s = st.slider("Timeout (seconds)", 5, 120, 30)

# Keep messages in session
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! Ask me anything 🙂"}
    ]

# Render history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def call_api(user_text: str):
    """
    Expected API contract (recommended):
    POST {API_URL}
    JSON: {"message": "<user_text>"}
    Response JSON: {"reply": "<assistant_text>"}
    """
    if not api_url_ui:
        return "❗Please set API URL in the sidebar."

    headers = {"Content-Type": "application/json"}
    # Optional key header (customize if your API uses different header)
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    payload = {"message": user_text}

    try:
        r = requests.post(api_url_ui, headers=headers, data=json.dumps(payload), timeout=timeout_s)
        r.raise_for_status()
        data = r.json()

        # flexible parsing
        if isinstance(data, dict):
            if "reply" in data:
                return str(data["reply"])
            if "response" in data:
                return str(data["response"])
            if "answer" in data:
                return str(data["answer"])
        return f"✅ API responded, but I couldn’t find 'reply'. Raw:\n\n```json\n{json.dumps(data, indent=2)}\n```"

    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP error: {e}\n\nResponse text:\n```\n{r.text}\n```"
    except Exception as e:
        return f"❌ Error calling API: {e}"

# Input
prompt = st.chat_input("Type your message…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = call_api(prompt)
            st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
