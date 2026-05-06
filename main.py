# =============================================================================
# main.py — Meridian Ops Assistant
# =============================================================================
# Streamlit re-runs this entire file from top to bottom every time the user
# interacts with the page (clicks a button, submits a message, etc.).
#
# Sections are arranged in the order they appear on screen:
#
#   1.  Config & Styles   — page setup, CSS, Supabase client
#   2.  Logout            — clears session when "Sign out" is clicked
#   3.  Login Gate        — shows the login form if the user isn't signed in
#   ──  authenticated from here down  ──────────────────────────────────────
#   4.  Scroll Scripts    — invisible JS fixes for scroll behavior
#   5.  State Setup       — chat history, webhook URL, pending prompts
#   6.  Navbar            — fixed top bar with user email + sign-out link
#   7.  Hero              — welcome heading shown before the first message
#   8.  Chat History      — all previous messages rendered in order
#   9.  Chat Input        — text box pinned to the bottom of the screen
#   10. Response Flow     — handles a new message end-to-end
# =============================================================================

import os
from dotenv import load_dotenv
load_dotenv(override=True)  # loads variables from the .env file into os.environ

import streamlit as st
from PIL import Image
from supabase import create_client

# All HTML, JavaScript, and visual rendering functions live in ui_components.py.
# Keeping them there makes this file easy to read at a glance.
from ui_components import (
    inject_scroll_scripts,
    render_login_page,
    render_navbar,
    render_hero_section,
    render_user_message,
    render_assistant_message,
    scroll_to_last_bubble,
    fetch_and_stream,
)


# =============================================================================
# 1. CONFIG & STYLES
# =============================================================================

# Sets the browser tab title, favicon, and page width
st.set_page_config(
    page_title="Meridian Ops Assistant",
    page_icon=Image.open("images/favicon.png"),
    layout="centered",
)

# Loads style.css — controls fonts, colors, the navbar, chat bubbles, etc.
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Creates the Supabase database connection.
# @st.cache_resource means it's only created once, not on every page rerun.
@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"],
    )


# =============================================================================
# 2. LOGOUT
# =============================================================================
# The "Sign out" link in the navbar navigates the browser to ?logout=1.
# On the next rerun, Streamlit sees that URL parameter here, wipes the
# session, and reloads — sending the user back to the login screen.

if st.query_params.get("logout"):
    try:
        get_supabase().auth.sign_out()
    except Exception:
        pass
    st.session_state.clear()  # removes all saved chat history and auth info
    st.query_params.clear()   # removes ?logout=1 from the URL
    st.rerun()                # triggers a fresh page load


# =============================================================================
# 3. LOGIN GATE
# =============================================================================
# If the user hasn't logged in yet, render the login form and stop here.
# st.stop() prevents every line below from running until they authenticate.

if not st.session_state.get("authenticated"):
    render_login_page(get_supabase())
    st.stop()


# =============================================================================
# AUTHENTICATED — everything below only runs for signed-in users
# =============================================================================


# =============================================================================
# 4. SCROLL SCRIPTS
# =============================================================================
# Injects invisible JavaScript that prevents the page from auto-scrolling
# and adds the scroll-to-bottom chevron button. See ui_components.py.

inject_scroll_scripts()


# =============================================================================
# 5. STATE SETUP
# =============================================================================
# st.session_state is a dictionary that persists between reruns for a given
# browser tab. We use it to remember the conversation and the logged-in user.

# The n8n webhook URL is read from the .env file
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

# Initialize the chat history list on the very first load
if "messages" not in st.session_state:
    st.session_state.messages = []

# Suggestion buttons write to pending_prompt; we read and remove it here
# so it's used exactly once as the prompt for this rerun
pending = st.session_state.pop("pending_prompt", None)

# True only before the user has sent any messages in this session
is_empty_chat = (len(st.session_state.messages) == 0 and pending is None)


# =============================================================================
# 6. NAVBAR  ← top of the screen
# =============================================================================

render_navbar(user_email=st.session_state.get("user_email", ""))


# =============================================================================
# 7. HERO / WELCOME SCREEN  ← shown before the first message
# =============================================================================

# st.empty() creates a named placeholder we can clear later when chat begins
header_slot = st.empty()

if is_empty_chat:
    with header_slot.container():
        render_hero_section()


# =============================================================================
# 8. CHAT HISTORY  ← all previous messages, top to bottom
# =============================================================================

for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        # add_spacer=False on the very first message so there's no extra gap
        render_user_message(msg["content"], add_spacer=(i > 0))
    else:
        render_assistant_message(msg["content"])


# =============================================================================
# 9. CHAT INPUT  ← pinned to the bottom of the screen by Streamlit
# =============================================================================

user_input = st.chat_input("Ask anything about your operations...")

# If a suggestion button was clicked, use that instead of the typed input
prompt = pending or user_input


# =============================================================================
# 10. RESPONSE FLOW  ← runs only when there is a new prompt to process
# =============================================================================

if prompt:

    # Clear the hero section now that the conversation has started
    if is_empty_chat:
        header_slot.empty()

    # Save and display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})
    render_user_message(prompt, add_spacer=(len(st.session_state.messages) > 1))

    # Smooth-scroll the new bubble into view
    scroll_to_last_bubble()

    # Call the n8n webhook and stream the response back to the screen
    response = fetch_and_stream(
        prompt=prompt,
        webhook_url=N8N_WEBHOOK_URL,
        webhook_secret=st.secrets["webhook"]["secret"],
    )

    # Save the assistant's reply so it appears on future reruns
    st.session_state.messages.append({"role": "assistant", "content": response})
