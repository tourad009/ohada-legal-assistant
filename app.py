import streamlit as st
from rag_pipeline import generate_answer_stream, rag_chain
import time
import html

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="OhadAI ⚖️", page_icon="⚖️", layout="wide")
# minimal safety: ensure session keys exist
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, text)
if "suggestions_visible" not in st.session_state:
    st.session_state.suggestions_visible = True

# -----------------------------
# STYLES & JS (smart autoscroll)
# -----------------------------
st.markdown(
    """
<style>
/* --- Fonts & layout --- */
:root{
  --bg:#0f1724;
  --card:#0b1220;
  --accent:#7c3aed;
  --muted:#94a3b8;
  --bubble-user:#0b1220;
  --bubble-user-text:#ffffff;
  --bubble-assistant:#ffffff;
  --bubble-assistant-text:#0b1220;
  --maxwidth:900px;
}
html, body, [data-testid="stAppViewContainer"]{
  background: linear-gradient(180deg,#f7fafc 0%, #eef2f7 100%) !important;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}

/* App centering */
.app-wrap {
  max-width: var(--maxwidth);
  margin: 14px auto 80px auto;
  padding: 0 16px;
}

/* header */
.header {
  display:flex;
  align-items:center;
  gap:12px;
  margin-bottom: 10px;
}
.header .logo {
  width:52px;
  height:52px;
  border-radius:12px;
  background:linear-gradient(135deg,var(--accent),#4f46e5);
  display:flex;
  align-items:center;
  justify-content:center;
  color:white;
  font-weight:700;
  box-shadow: 0 6px 18px rgba(15,23,42,0.12);
}
.header h1 {
  margin:0;
  font-size:1.25rem;
}
.header p { margin:0; color:var(--muted); font-size:0.9rem; }

/* ascii art */
.ascii {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace;
  color: #334155;
  font-size: 11px;
  margin-top:8px;
}

/* chat area */
.chat-frame {
  border-radius:12px;
  background: white;
  padding:12px;
  box-shadow: 0 8px 30px rgba(2,6,23,0.06);
  max-height: calc(100vh - 220px);
  overflow: hidden;
  display:flex;
  flex-direction:column;
}

/* messages area (scroll) */
.messages {
  overflow-y: auto;
  padding: 10px;
  display:flex;
  flex-direction:column;
  gap:8px;
  scroll-behavior: smooth;
}

/* message row */
.row {
  display:flex;
  gap:10px;
  align-items:flex-end;
}
.row.user { justify-content:flex-end; }
.row .avatar {
  width:36px; height:36px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  font-weight:600;
}
.avatar.user { background:linear-gradient(135deg,#0ea5e9,#0284c7); color:white; }
.avatar.bot { background:#f1f5f9; color:#0f1724; border:1px solid #e6edf3; }

/* bubble */
.bubble {
  max-width: 76%;
  padding:10px 12px;
  border-radius:12px;
  line-height:1.4;
  white-space: pre-wrap;
  box-shadow: 0 6px 14px rgba(2,6,23,0.04);
}
.user .bubble {
  background: var(--bubble-user);
  color: var(--bubble-user-text);
  border-bottom-right-radius:6px;
}
.bot .bubble {
  background: var(--bubble-assistant);
  color: var(--bubble-assistant-text);
  border-bottom-left-radius:6px;
  border: 1px solid #eef2f7;
}

/* streaming cursor */
.cursor {
  display:inline-block;
  width:8px; height:14px; background:#cbd5e1; margin-left:6px; border-radius:2px;
  animation: blink 1s steps(2,start) infinite;
}
@keyframes blink { to { opacity:0.1 } }

/* suggestions */
.suggestions { display:flex; gap:8px; padding:10px 6px; flex-wrap:wrap; }
.suggestion {
  background: transparent;
  border:1px solid #e6eef8;
  padding:8px 12px;
  border-radius:999px;
  cursor:pointer;
  color:#0f1724;
  font-weight:500;
}
.suggestion:hover { background:#eef2ff; }

/* input area (sticky) */
.input-area {
  position: sticky;
  bottom: 0;
  background: transparent;
  padding-top:10px;
  display:flex;
  gap:8px;
  align-items:center;
}
.input-box {
  flex:1;
  display:flex;
  gap:8px;
  align-items:center;
}
.send-btn {
  background: linear-gradient(135deg,var(--accent),#4f46e5);
  color:white;
  border:none;
  padding:8px 12px;
  border-radius:8px;
  cursor:pointer;
  font-weight:600;
}
.small-muted { color:var(--muted); font-size:12px; margin-left:8px; }
</style>

<script>
/* Smart autoscroll controller:
   - window._ohadai_autoScroll: boolean (true by default)
   - If user scrolls up (not at bottom), autoScroll=false.
   - If user scrolls to bottom again, autoScroll=true.
   - Expose function scrollIfAllowed() to be called after messages update.
*/
window._ohadai_autoScroll = true;
window._ohadai_scroll_threshold = 60; // px

function __ohadai_install_scroll_listener(chatId) {
  const el = document.getElementById(chatId);
  if (!el || el._ohadai_installed) return;
  el._ohadai_installed = true;
  el.addEventListener('scroll', () => {
    const atBottom = (el.scrollHeight - el.scrollTop - el.clientHeight) < window._ohadai_scroll_threshold;
    window._ohadai_autoScroll = atBottom;
    // send small hint to Streamlit (works if streamlit exposes global)
    if (typeof window.streamlitDebug !== "undefined") {
      // noop
    }
  }, {passive:true});
}

function scrollIfAllowed(chatId) {
  const el = document.getElementById(chatId);
  if (!el) return;
  if (window._ohadai_autoScroll) {
    el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
  }
}
</script>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# HEADER with ASCII art mini-logo
# -----------------------------
st.markdown('<div class="app-wrap">', unsafe_allow_html=True)
st.markdown(
    """
    <div class="header">
      <div class="logo">OA</div>
      <div>
        <h1>OhadAI <span style="color:#6b7280; font-weight:400">⚖️ Assistant OHADA</span></h1>
        <div class="small-muted">Réponses juridiques basées sur ton corpus — interface optimisée</div>
      </div>
    </div>
    <pre class="ascii">  ____  _   _  _   _  _   _   ___ 
 / __ \| | | || \ | || \ | | / _ \\
| |  | | | | ||  \| ||  \| || | | |
| |  | | | | || . ` || . ` || | | |
| |__| | |_| || |\  || |\  || |_| |
 \____/ \___/ |_| \_||_| \_| \___/ </pre>
    """,
    unsafe_allow_html=True,
)

# -----------------------------
# CHAT FRAME + SUGGESTIONS
# -----------------------------
st.markdown('<div class="chat-frame">', unsafe_allow_html=True)

# Suggestions (only shown when no history)
if st.session_state.suggestions_visible and not st.session_state.chat_history:
    st.markdown('<div class="suggestions">', unsafe_allow_html=True)
    presets = [
        "Procédure d'arbitrage OHADA",
        "SARL : société de personnes ou de capitaux ?",
        "Que dit le droit OHADA sur cession de parts ?",
    ]
    for s in presets:
        # use a tiny JS call to set input value
        st.markdown(
            f'<button class="suggestion" onclick="window.streamlitSetComponentValue && window.streamlitSetComponentValue({html.escape(repr(s))});document.querySelector(\\'input[data-testid=\\\"stTextInput\\"]\\')?.focus();">{s}</button>',
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)

# Messages container
st.markdown('<div id="messages" class="messages"></div>', unsafe_allow_html=True)

# Install scroll listener (once)
st.markdown(
    """
<script>
__ohadai_install_scroll_listener('messages');
</script>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# RENDER EXISTING HISTORY (server-side)
# -----------------------------
def _render_history():
    # We'll render HTML directly into the #messages div by building markup
    html_parts = []
    for role, text in st.session_state.chat_history:
        safe_text = html.escape(text)
        if role == "user":
            html_parts.append(
                f'''
                <div class="row user">
                  <div class="bubble" style="background:linear-gradient(135deg,#0ea5e9,#0284c7); color:white; border:none;">{safe_text}</div>
                  <div class="avatar user">U</div>
                </div>
                '''
            )
        else:
            html_parts.append(
                f'''
                <div class="row bot">
                  <div class="avatar bot">⚖️</div>
                  <div class="bubble">{safe_text}</div>
                </div>
                '''
            )
    if html_parts:
        joined = "\n".join(html_parts)
        st.markdown(f"""
        <script>
        const m = document.getElementById('messages');
        if (m) {{
            m.innerHTML = `{joined}`;
            // after reinserting, scroll if allowed
            scrollIfAllowed('messages');
        }}
        </script>
        """, unsafe_allow_html=True)
    else:
        # empty placeholder
        st.markdown(
            """
            <script>
            const m = document.getElementById('messages');
            if (m && m.innerHTML.trim() === '') {
                m.innerHTML = '<div style="color:#94a3b8; padding:12px;">Posez votre question — ex: "Procédure d\\'arbitrage OHADA"</div>';
            }
            </script>
            """,
            unsafe_allow_html=True,
        )


_render_history()

# -----------------------------
# INPUT AREA (sticky footer inside the chat-frame)
# -----------------------------
st.markdown(
    """
    <div class="input-area">
      <div class="input-box">
    """,
    unsafe_allow_html=True,
)

# Use native Streamlit input to keep accessibility & keyboard support
user_question = st.text_input("", key="ohadai_input", placeholder="Posez votre question juridique...")
send_col = st.empty()
# render send button on the right (HTML button that triggers JS to submit using Enter key effect)
st.markdown(
    """
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
      <button class="send-btn" id="ohadai_send">Envoyer</button>
      <div class="small-muted">Streaming · OHADA</div>
    </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# JS: connect the send button to pressing Enter in the Streamlit text input (works in most browsers)
st.markdown(
    """
<script>
const sendBtn = document.getElementById('ohadai_send');
if (sendBtn) {
  sendBtn.addEventListener('click', () => {
    const el = document.querySelector('input[placeholder="Posez votre question juridique..."]');
    if (el) {
      el.dispatchEvent(new KeyboardEvent('keydown',{'key':'Enter'}));
    }
  });
}
</script>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# HANDLE SUBMISSION & STREAMING
# -----------------------------
if user_question and user_question.strip():
    q = user_question.strip()
    # hide suggestions once user starts
    st.session_state.suggestions_visible = False
    # append immediately to history (user bubble)
    st.session_state.chat_history.append(("user", q))
    # clear the input key so the UI empties
    st.session_state["ohadai_input"] = ""

    # render user message immediately in page DOM
    safe_q = html.escape(q)
    st.markdown(
        f"""
        <script>
        const m = document.getElementById('messages');
        if (m) {{
          // append user row
          m.innerHTML += `
            <div class="row user">
              <div class="bubble" style="background:linear-gradient(135deg,#0ea5e9,#0284c7); color:white; border:none;">{safe_q}</div>
              <div class="avatar user">U</div>
            </div>
          `;
          scrollIfAllowed('messages');
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

    # prepare placeholder assistant bubble (we'll update it chunk by chunk)
    placeholder_id = f"assistant_{int(time.time()*1000)}"
    st.markdown(
        f"""
        <script>
        const m = document.getElementById('messages');
        if (m) {{
          m.innerHTML += `
            <div class="row bot" id="{placeholder_id}_row">
              <div class="avatar bot">⚖️</div>
              <div class="bubble" id="{placeholder_id}">…<span class="cursor"></span></div>
            </div>
          `;
          scrollIfAllowed('messages');
        }}
        </script>
        """,
        unsafe_allow_html=True,
    )

    # STREAM the answer from the rag pipeline
    full_response = ""
    try:
        for chunk in generate_answer_stream(q, rag_chain):
            # update aggregator
            full_response = chunk
            safe_chunk = html.escape(full_response).replace("\n", "<br/>")
            # replace innerHTML of placeholder
            st.markdown(
                f"""
                <script>
                const el = document.getElementById('{placeholder_id}');
                if (el) {{
                  el.innerHTML = `{safe_chunk}`;
                }}
                scrollIfAllowed('messages');
                </script>
                """,
                unsafe_allow_html=True,
            )
        # streaming finished: remove cursor by re-setting bubble (and add final newline formatting)
        final_safe = html.escape(full_response).replace("\n", "<br/>")
        st.markdown(
            f"""
            <script>
            const el = document.getElementById('{placeholder_id}');
            if (el) {{
               el.innerHTML = `{final_safe}`;
            }}
            scrollIfAllowed('messages');
            </script>
            """,
            unsafe_allow_html=True,
        )
        # finally add to session history
        st.session_state.chat_history.append(("assistant", full_response))
    except Exception as e:
        err = f"Erreur lors de la génération : {str(e)}"
        st.session_state.chat_history.append(("assistant", err))
        st.markdown(
            f"""
            <script>
            const el = document.getElementById('{placeholder_id}');
            if (el) {{
               el.innerHTML = `{html.escape(err)}`;
            }}
            scrollIfAllowed('messages');
            </script>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# Ensure scroll listener exists and final scroll (in case JS wasn't loaded earlier)
# -----------------------------
st.markdown(
    """
<script>
__ohadai_install_scroll_listener('messages');
scrollIfAllowed('messages');
</script>
""",
    unsafe_allow_html=True,
)

# close outer wrapper
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Short credits / small control (optional)
# -----------------------------
st.markdown(
    """
    <div style="max-width:var(--maxwidth); margin:8px auto 48px auto; color:#475569; font-size:12px;">
      ⚠️ Prototype UI — Inspiré par bonnes pratiques Streamlit & composants chat — streaming pris en charge.
    </div>
    """,
    unsafe_allow_html=True,
)
