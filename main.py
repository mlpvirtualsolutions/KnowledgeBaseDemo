import base64
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

st.set_page_config(
    page_title="Meridian Ops Assistant",
    page_icon=Image.open("images/favicon.png"),
    layout="centered",
)

with open("images/logo.png", "rb") as f:
    img_b64 = base64.b64encode(f.read()).decode()

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

components.html("""<script>
(function(){
    var w = window.parent;
    if(!w || w._scrollKilled) return;
    w._scrollKilled = true;

    // 1. Kill all JS scroll functions
    w.scrollTo = w.scroll = w.scrollBy = function(){};
    w.Element.prototype.scrollIntoView = function(){};
    w.Element.prototype.scrollTo       = function(){};
    w.Element.prototype.scrollBy       = function(){};

    // 2. Kill the scrollTop setter so direct property writes are ignored
    ['HTMLElement', 'Element'].forEach(function(name){
        var proto = w[name] && w[name].prototype;
        if(!proto) return;
        var d = Object.getOwnPropertyDescriptor(proto, 'scrollTop');
        if(d && d.set) Object.defineProperty(proto, 'scrollTop',
            {get: d.get, set: function(){}, configurable: true});
    });

    // 3. Force overflow-anchor:none on every element so the browser's own
    //    scroll-anchoring algorithm never adjusts the viewport position
    function noAnchor(root){
        root.querySelectorAll('*').forEach(function(el){
            el.style.overflowAnchor = 'none';
        });
    }
    noAnchor(w.document);
    new w.MutationObserver(function(muts){
        muts.forEach(function(m){
            m.addedNodes.forEach(function(n){
                if(n.nodeType===1){
                    n.style.overflowAnchor='none';
                    noAnchor(n);
                }
            });
        });
    }).observe(w.document.body, {childList:true, subtree:true});
})();
</script>""", height=0)

N8N_WEBHOOK_URL = "https://mlpvirtualsolutions.app.n8n.cloud/webhook/d7ce584c-b36b-4f7a-b920-1a0383ba483c"

if "messages" not in st.session_state:
    st.session_state.messages = []

pending = st.session_state.pop("pending_prompt", None)
show_header = len(st.session_state.messages) == 0 and pending is None
header_placeholder = st.empty()

if show_header:
    with header_placeholder.container():
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
                    st.rerun()

        st.markdown("<div style='margin-bottom:20px'></div>", unsafe_allow_html=True)

AVATAR_HTML = f'<img src="data:image/png;base64,{img_b64}" class="assistant-avatar">'


def render_user(text):
    _, right = st.columns([0.22, 0.78])
    with right:
        st.markdown(f'<div class="user-bubble">{text}</div>', unsafe_allow_html=True)


def render_assistant(text):
    """Instant render for history replay."""
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    left, right = st.columns([0.06, 0.94])
    with left:
        st.markdown(AVATAR_HTML, unsafe_allow_html=True)
    with right:
        st.markdown(text)


def fetch_and_stream(prompt):
    """
    Single column layout:
      1. placeholder (empty) + spinner while fetching
      2. stream response into placeholder — no new elements added so scroll stays put
    """
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    left, right = st.columns([0.06, 0.94])
    with left:
        st.markdown(AVATAR_HTML, unsafe_allow_html=True)
    with right:
        # placeholder sits above the spinner; both are in the right column
        placeholder = st.empty()
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

        displayed = ""
        for i in range(0, len(response), 10):
            displayed += response[i:i + 10]
            placeholder.markdown(displayed)
            time.sleep(0.015)
        placeholder.markdown(response)

    return response


for message in st.session_state.messages:
    if message["role"] == "user":
        render_user(message["content"])
    else:
        render_assistant(message["content"])

chat_in = st.chat_input("Ask anything")
prompt = pending or chat_in

if prompt:
    if show_header:
        header_placeholder.empty()

    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user(prompt)

    response = fetch_and_stream(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
