import os
import json
import requests
import streamlit as st

st.set_page_config(page_title="Chatbot Demo", page_icon="💬")

st.title("💬 Chatbot Demo")
st.caption("Demo UI (Streamlit) calling your Databricks REST endpoint")

API_URL = os.getenv("API_URL", "").strip()
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "").strip()

with st.sidebar:
    st.header("Settings")
    api_url_ui = st.text_input("API URL", value=API_URL, placeholder="https://.../invocations")
    timeout_s = st.slider("Timeout (seconds)", 5, 300, 120)
    st.caption("Tip: Store API_URL and DATABRICKS_TOKEN in Streamlit Secrets.")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me anything 🙂"}]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def call_api(user_text: str):
    if not api_url_ui:
        return "❗Please set API URL in the sidebar."
    if not DATABRICKS_TOKEN:
        return "❗Missing DATABRICKS_TOKEN. Add it in Streamlit → Settings → Secrets."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    }

    payload = {
        "dataframe_split": {
            "columns": ["question"],
            "data": [[user_text]]
        }
    }

    st.sidebar.write("Sending payload:", payload)  # TEMP debug

    try:
        r = requests.post(api_url_ui, headers=headers, json=payload, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()

        if isinstance(data, dict) and "predictions" in data:
            preds = data["predictions"]
            return str(preds[0]) if isinstance(preds, list) and preds else str(preds)

        return f"✅ API responded. Raw:\n\n```json\n{json.dumps(data, indent=2)}\n```"

    except requests.exceptions.HTTPError as e:
        return f"❌ HTTP error: {e}\n\nResponse text:\n```\n{r.text}\n```"
    except Exception as e:
        return f"❌ Error calling API: {e}"


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
