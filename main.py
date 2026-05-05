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

with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

components.html("""<script>
(function(){
    var w = window.parent;
    if(!w || w._scrollKilled) return;
    w._scrollKilled = true;

    w.scrollTo = w.scroll = w.scrollBy = function(){};
    w.Element.prototype.scrollIntoView = function(){};
    w.Element.prototype.scrollTo       = function(){};
    w.Element.prototype.scrollBy       = function(){};

    ['HTMLElement', 'Element'].forEach(function(name){
        var proto = w[name] && w[name].prototype;
        if(!proto) return;
        var d = Object.getOwnPropertyDescriptor(proto, 'scrollTop');
        if(d && d.set) Object.defineProperty(proto, 'scrollTop',
            {get: d.get, set: function(){}, configurable: true});
    });

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

    function setupTextarea(ta){
        if(ta._autoResize) return;
        ta._autoResize = true;
        ta.style.overflowY = 'hidden';
        ta.style.resize    = 'none';
        function resize(){
            ta.style.height = 'auto';
            ta.style.height = ta.scrollHeight + 'px';
        }
        ta.addEventListener('input', resize);
        resize();
    }
    function findTextareas(){
        w.document.querySelectorAll('[data-testid="stChatInputTextArea"]')
                  .forEach(setupTextarea);
    }
    findTextareas();
    new w.MutationObserver(findTextareas)
        .observe(w.document.body, {childList:true, subtree:true});
})();
</script>""", height=0)

N8N_WEBHOOK_URL = "https://mlpvirtualsolutions.app.n8n.cloud/webhook/d7ce584c-b36b-4f7a-b920-1a0383ba483c"

if "messages" not in st.session_state:
    st.session_state.messages = []

pending = st.session_state.pop("pending_prompt", None)
show_header = len(st.session_state.messages) == 0 and pending is None

# Navbar always rendered — position:fixed keeps it visible regardless of DOM position
st.markdown("""
<div class="app-navbar">
  <div class="nav-brand">LOGI<span class="nav-brand-accent">DEX</span></div>
  <div class="nav-links">
    <span class="nav-link active">Chat</span>
    <span class="nav-link">Dashboard</span>
    <span class="nav-link">Handbook</span>
    <span class="nav-link">Team</span>
  </div>
  <span class="nav-company">Meridian Freight</span>
</div>
""", unsafe_allow_html=True)

header_placeholder = st.empty()

if show_header:
    with header_placeholder.container():
        st.markdown("""
<div class="hero-label">Meridian Ops Assistant</div>
<h1 class="hero-heading">What do you need to <span class="hero-accent">know?</span></h1>
<p class="hero-subtitle">Step-by-step answers pulled directly from your operations handbook.</p>
""", unsafe_allow_html=True)

        suggestions = [
            "I just got a handoff from sales — what should I do?",
            "How do I source and vet a carrier?",
            "What do I do if a load is late or missing?",
        ]
        for i, sug in enumerate(suggestions):
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_prompt = sug
                st.rerun()

        st.markdown("""
<p class="app-footer">Powered by <span class="app-footer-accent">Logidex</span></p>
""", unsafe_allow_html=True)

ASSISTANT_LABEL = '<div class="assistant-label"><span class="assistant-dot">●</span> LOGIDEX</div>'


def render_user(text):
    _, right = st.columns([0.22, 0.78])
    with right:
        st.markdown(f'<div class="user-bubble">{text}</div>', unsafe_allow_html=True)


def render_assistant(text):
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    st.markdown(ASSISTANT_LABEL, unsafe_allow_html=True)
    st.markdown(text)


def fetch_and_stream(prompt):
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    st.markdown(ASSISTANT_LABEL, unsafe_allow_html=True)
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

chat_in = st.chat_input("Ask anything about your operations...")
prompt = pending or chat_in

if prompt:
    if show_header:
        header_placeholder.empty()

    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user(prompt)

    response = fetch_and_stream(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
