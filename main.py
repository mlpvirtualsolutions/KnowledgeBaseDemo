import base64
import requests
import streamlit as st
from PIL import Image

st.set_page_config(layout="centered")

with open("images/logo.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

N8N_WEBHOOK_URL = "https://mlpvirtualsolutions.app.n8n.cloud/webhook/d7ce584c-b36b-4f7a-b920-1a0383ba483c"

if "messages" not in st.session_state:
    st.session_state.messages = []

LOGO_PATH = "images/logo.png"
logo_avatar = Image.open(LOGO_PATH).resize((42, 42))
user_avatar = Image.open("images/user.png").resize((42, 42))

show_header = len(st.session_state.messages) == 0

if show_header:
    st.markdown(f"""
<div style="text-align:center; padding-top:8px;">
  <img class="logo-img" src="data:image/png;base64,{img_b64}">
</div>
<h1 class="centered-header">Meridian Ops Assistant</h1>
<p class="centered-sub">Your internal guide for the Meridian Brokerage Operations team. Ask anything about load execution, McLeod TMS, carrier sourcing, vetting, tracking, invoicing, and escalations — and get step-by-step answers pulled directly from the Operations Team Knowledge Base.</p>
""", unsafe_allow_html=True)

    suggestions = [
        "I just got a handoff from sales — what should I do?",
        "How do I source and vet a carrier?",
        "What do I do if a load is late or missing?",
    ]
    cols = st.columns(3)
    for i, (col, sug) in enumerate(zip(cols, suggestions)):
        with col:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_prompt = sug

    st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

for message in st.session_state.messages:
    avatar = logo_avatar if message["role"] == "assistant" else user_avatar
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

pending = st.session_state.pop("pending_prompt", None)
chat_in = st.chat_input("Ask anything")
prompt = pending or chat_in

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=user_avatar):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=logo_avatar):
        with st.spinner("Thinking..."):
            try:
                resp = requests.get(
                    N8N_WEBHOOK_URL,
                    params={"message": prompt},
                    auth=(st.secrets["auth"]["username"], st.secrets["auth"]["password"]),
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, list) and data:
                    response = data[0].get("output") or data[0].get("message") or str(data[0])
                elif isinstance(data, dict):
                    response = data.get("output") or data.get("message") or data.get("text") or str(data)
                else:
                    response = str(data)
            except Exception as e:
                response = f"Error contacting n8n webhook: {e}"
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
