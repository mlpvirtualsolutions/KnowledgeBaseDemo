# =============================================================================
# ui_components.py
# =============================================================================
# All HTML snippets, JavaScript injections, and UI rendering functions.
# Imported by main.py — keeping this code here lets main.py stay clean.
# You rarely need to edit this file unless you're changing the visual design.
# =============================================================================

import time
import requests
import streamlit as st
import streamlit.components.v1 as components


# =============================================================================
# SECTION 1 — SCROLL BEHAVIOR SCRIPTS
# =============================================================================
# These scripts are injected as invisible iframes (height=0).
# They override Streamlit's built-in scroll behavior so the chat page
# doesn't jump to the top or bottom unexpectedly when new content loads.
# =============================================================================

# Disables Streamlit's auto-scroll and saves two helper functions on the window:
#   w._scrollTo(element)    — smooth-scrolls to any element on the page
#   w._setScrollTop(el, v)  — sets the scroll position without triggering interceptors
_SCROLL_KILL_SCRIPT = """<script>
(function(){
    var w = window.parent;
    if(!w || w._scrollKilled) return;
    w._scrollKilled = true;

    var _origSIV = w.Element.prototype.scrollIntoView;
    w._scrollTo = function(el, opts) {
        _origSIV.call(el, opts || {behavior: 'smooth', block: 'start'});
    };

    var _stDesc = Object.getOwnPropertyDescriptor(w.HTMLElement.prototype, 'scrollTop')
                || Object.getOwnPropertyDescriptor(w.Element.prototype, 'scrollTop');
    var _origSetST = (_stDesc || {}).set;
    w._setScrollTop = function(el, v) { if (_origSetST) _origSetST.call(el, v); };

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
</script>"""

# Adds two visual extras just above the chat input bar:
#   1. A subtle gradient that softly hides content near the bottom edge
#   2. A circular chevron button that appears when the user has scrolled up,
#      clicking it returns them to the bottom of the conversation
_SCROLL_BTN_SCRIPT = """<script>
(function(){
    var w = window.parent;

    if (!w.document.getElementById('logidex-fade')) {
        var fade = w.document.createElement('div');
        fade.id = 'logidex-fade';
        fade.style.cssText = 'position:fixed;left:0;right:0;height:44px;background:linear-gradient(to bottom,transparent,#edf1f8);pointer-events:none;z-index:9990;bottom:64px;';
        w.document.body.appendChild(fade);

        function positionFade() {
            var sb = w.document.querySelector('[data-testid="stBottom"]');
            if (!sb) { setTimeout(positionFade, 200); return; }
            var fromBottom = w.innerHeight - sb.getBoundingClientRect().top;
            fade.style.bottom = fromBottom + 'px';
        }
        setTimeout(positionFade, 400);
        w.addEventListener('resize', positionFade);
    }

    if (!w.document.getElementById('logidex-scroll-btn')) {
        var btn = w.document.createElement('button');
        btn.id = 'logidex-scroll-btn';
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3.5 5.5L8 10.5L12.5 5.5" stroke="#475569" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        btn.style.cssText = 'position:fixed;bottom:88px;left:50%;transform:translateX(-50%);width:36px;height:36px;border-radius:50%;background:#fff;border:1px solid #e2e8f0;box-shadow:0 2px 8px rgba(0,0,0,0.15);display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:9998;opacity:0;pointer-events:none;transition:opacity 0.2s ease;padding:0;';
        w.document.body.appendChild(btn);

        function findScrollable() {
            var bc = w.document.querySelector('.block-container');
            if (!bc) return w.document.documentElement;
            var node = bc.parentElement;
            while (node && node !== w.document.documentElement) {
                var ov = w.getComputedStyle(node).overflowY;
                if (ov === 'auto' || ov === 'scroll' || ov === 'overlay') return node;
                node = node.parentElement;
            }
            return w.document.documentElement;
        }

        var sc = null;
        function getScrollable() { if (!sc) sc = findScrollable(); return sc; }

        function checkVisibility() {
            var s = getScrollable();
            var atBottom = s.scrollTop + s.clientHeight >= s.scrollHeight - 80;
            btn.style.opacity = atBottom ? '0' : '1';
            btn.style.pointerEvents = atBottom ? 'none' : 'auto';
        }

        function init() {
            var s = findScrollable();
            if (s) { sc = s; s.addEventListener('scroll', checkVisibility); checkVisibility(); }
            else setTimeout(init, 300);
        }
        init();

        btn.addEventListener('click', function() {
            var s = getScrollable();
            var start = s.scrollTop;
            var end = s.scrollHeight - s.clientHeight;
            var duration = 300;
            var startTime = null;
            function step(ts) {
                if (!startTime) startTime = ts;
                var p = Math.min((ts - startTime) / duration, 1);
                var ease = 1 - Math.pow(1 - p, 3);
                if (w._setScrollTop) w._setScrollTop(s, start + (end - start) * ease);
                if (p < 1) w.requestAnimationFrame(step);
            }
            w.requestAnimationFrame(step);
        });
    }
})();
</script>"""

# Fires 300ms after a message is sent, scrolling the newest user bubble
# into view using the helper function saved by _SCROLL_KILL_SCRIPT above.
_SCROLL_TO_BUBBLE_SCRIPT = """<script>
setTimeout(function(){
    var w = window.parent;
    var bubbles = w.document.querySelectorAll('.user-bubble');
    if (!bubbles.length) return;
    if (w._scrollTo) w._scrollTo(bubbles[bubbles.length - 1]);
}, 300);
</script>"""


def inject_scroll_scripts():
    """Injects the scroll-disable and scroll-to-bottom-button scripts into the page."""
    components.html(_SCROLL_KILL_SCRIPT, height=0)
    components.html(_SCROLL_BTN_SCRIPT,  height=0)


def scroll_to_last_bubble():
    """Smooth-scrolls the most recent user message bubble into view."""
    components.html(_SCROLL_TO_BUBBLE_SCRIPT, height=0)


# =============================================================================
# SECTION 2 — LOGIN PAGE
# =============================================================================
# Displayed to any visitor who is not yet signed in.
# =============================================================================

def render_login_page(supabase):
    """
    Draws the centered login card and handles the sign-in flow.

    Parameters:
        supabase — the Supabase client (created in main.py via get_supabase())

    On a successful login:
        - st.session_state.authenticated  is set to True
        - st.session_state.user_email     stores the user's email address
        - st.rerun() reloads the app, which now passes the auth gate
    """
    # Push content below the navbar area
    st.markdown('<div style="height:56px"></div>', unsafe_allow_html=True)

    # Three-column layout to center the card on the page
    _, col, _ = st.columns([1, 1.2, 1])
    with col:

        # Brand logo and tagline
        st.markdown("""
<div style="text-align:center;margin-bottom:28px;">
  <div style="font-size:2rem;font-weight:800;letter-spacing:0.04em;color:#0f172a;">
    LOGI<span style="color:#3b82f6;">DEX</span>
  </div>
  <div style="color:#64748b;font-size:0.875rem;margin-top:8px;">
    Sign in to Meridian Ops Assistant
  </div>
</div>
""", unsafe_allow_html=True)

        # Streamlit form — groups the fields so the page only reruns on submit,
        # not on every keystroke
        with st.form("login_form", border=False):
            email    = st.text_input("Email address", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            st.markdown('<div style="height:4px"></div>', unsafe_allow_html=True)
            submitted = st.form_submit_button("Sign In", use_container_width=True)

        # Process the form after the button is clicked
        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                with st.spinner("Signing in..."):
                    try:
                        result = supabase.auth.sign_in_with_password({
                            "email":    email,
                            "password": password,
                        })
                        st.session_state.authenticated = True
                        st.session_state.user_email    = result.user.email
                        st.rerun()
                    except Exception:
                        st.error("Invalid email or password.")


# =============================================================================
# SECTION 3 — NAVBAR
# =============================================================================
# Fixed dark bar at the top of every authenticated page.
# =============================================================================

def render_navbar(user_email: str):
    """
    Renders the top navigation bar.

    Parameters:
        user_email — the logged-in user's email, shown on the right side

    The 'Sign out' link navigates to ?logout=1.
    main.py detects that query parameter and clears the session.
    """
    st.markdown(f"""
<div class="app-navbar">
  <div class="nav-brand">LOGI<span class="nav-brand-accent">DEX</span></div>
  <div class="nav-links">
    <span class="nav-link active">Chat</span>
    <span class="nav-link">Dashboard</span>
    <span class="nav-link">Handbook</span>
    <span class="nav-link">Team</span>
  </div>
  <div style="display:flex;align-items:center;gap:10px;">
    <span class="nav-company">{user_email}</span>
    <a href="?logout=1" class="nav-signout">Sign out</a>
  </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# SECTION 4 — HERO / WELCOME SCREEN
# =============================================================================
# Only shown before the user has sent their first message.
# =============================================================================

def render_hero_section():
    """
    Renders the welcome heading, subtitle, and three suggestion buttons.

    When a suggestion button is clicked:
        - The text is saved to st.session_state.pending_prompt
        - st.rerun() fires, and main.py picks it up as the next prompt
    """
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
    for i, suggestion in enumerate(suggestions):
        if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_prompt = suggestion
            st.rerun()

    st.markdown("""
<p class="app-footer">Powered by <span class="app-footer-accent">Logidex</span></p>
""", unsafe_allow_html=True)


# =============================================================================
# SECTION 5 — CHAT MESSAGES
# =============================================================================
# Renderers for individual user and assistant messages.
# =============================================================================

# Label placed above every assistant response
_ASSISTANT_LABEL = (
    '<div class="assistant-label">'
    '<span class="assistant-dot">●</span> LOGIDEX'
    '</div>'
)


def render_user_message(text: str, add_spacer: bool = True):
    """
    Renders a right-aligned dark bubble containing the user's message.

    Parameters:
        text       — the message text to display
        add_spacer — adds vertical space above the bubble; set to False
                     for the very first message so there's no extra gap
    """
    if add_spacer:
        st.markdown('<div class="user-spacer"></div>', unsafe_allow_html=True)

    # Two-column layout: empty left column pushes the bubble to the right side
    _, right = st.columns([0.22, 0.78])
    with right:
        st.markdown(f'<div class="user-bubble">{text}</div>', unsafe_allow_html=True)


def render_assistant_message(text: str):
    """
    Renders a LOGIDEX label followed by the assistant's response.
    The response is rendered as markdown, so bold, lists, and headings work.
    """
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    st.markdown(_ASSISTANT_LABEL, unsafe_allow_html=True)
    st.markdown(text)


# =============================================================================
# SECTION 6 — WEBHOOK CALL & STREAMING
# =============================================================================
# Sends the user's message to n8n and streams the reply back to the screen.
# =============================================================================

def fetch_and_stream(prompt: str, webhook_url: str, webhook_secret: str) -> str:
    """
    Calls the n8n webhook with the user's prompt and streams the response.

    Steps:
      1. Show the LOGIDEX label and reserve an empty slot on the screen
      2. Call the webhook and wait for the full response (up to 30 seconds)
      3. Reveal the response 10 characters at a time to simulate streaming
      4. Return the full response string so main.py can save it to history

    Parameters:
        prompt         — the user's message
        webhook_url    — the n8n webhook URL (from the .env file)
        webhook_secret — the shared secret header value (from secrets.toml)
    """
    st.markdown('<div class="msg-spacer"></div>', unsafe_allow_html=True)
    st.markdown(_ASSISTANT_LABEL, unsafe_allow_html=True)

    # Placeholder is an empty slot we update repeatedly to create the streaming effect
    placeholder = st.empty()

    with st.spinner("Thinking..."):
        try:
            resp = requests.get(
                webhook_url,
                params={"message": prompt},
                headers={"Logidex-Webhook-Secret": webhook_secret},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            # n8n may return a list or a dict — extract the text either way
            if isinstance(data, list) and data:
                response = data[0].get("output") or data[0].get("message") or str(data[0])
            elif isinstance(data, dict):
                response = data.get("output") or data.get("message") or data.get("text") or str(data)
            else:
                response = str(data)

        except Exception as e:
            response = f"Error contacting n8n webhook: {e}"

    # Streaming effect: append 10 characters per tick and re-render the placeholder
    displayed = ""
    for i in range(0, len(response), 10):
        displayed += response[i:i + 10]
        placeholder.markdown(displayed)
        time.sleep(0.015)

    # Final render ensures the complete, exact text is shown
    placeholder.markdown(response)

    return response
