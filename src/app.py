import streamlit as st
from agent import triage_vulnerability
from pathlib import Path
from datetime import datetime
import json
import uuid

st.set_page_config(
    page_title="Bug Bounty Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="auto"
)

HISTORY_FILE = Path("data/conversations.json")
HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


# =========================
# Persistent conversation storage
# =========================

def load_conversations():
    try:
        if HISTORY_FILE.exists():
            data = json.loads(HISTORY_FILE.read_text())
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_conversations(conversations):
    HISTORY_FILE.write_text(
        json.dumps(conversations, indent=2, ensure_ascii=False)
    )


def new_conversation():
    return {
        "id": uuid.uuid4().hex[:10],
        "title": "New finding",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": [
            {
                "role": "assistant",
                "content": (
                    "Hey! 👋\n\n"
                    "I'm your **Bug Bounty Triage Agent**. "
                    "Describe a vulnerability and I'll analyze it using "
                    "**Hindsight memory** to look for previous findings, "
                    "patterns, duplicates, and related triage decisions."
                )
            }
        ]
    }


if "conversations" not in st.session_state:
    st.session_state.conversations = load_conversations()

if "active_id" not in st.session_state:
    if st.session_state.conversations:
        st.session_state.active_id = st.session_state.conversations[-1]["id"]
    else:
        first = new_conversation()
        st.session_state.conversations.append(first)
        st.session_state.active_id = first["id"]
        save_conversations(st.session_state.conversations)


def get_active_conversation():
    for conversation in st.session_state.conversations:
        if conversation["id"] == st.session_state.active_id:
            return conversation
    return None


def create_new_conversation():
    conversation = new_conversation()
    st.session_state.conversations.append(conversation)
    st.session_state.active_id = conversation["id"]
    save_conversations(st.session_state.conversations)


# =========================
# Custom UI
# =========================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(circle at 50% -10%, #202532 0%, #0e1015 38%, #0b0d11 75%);
}

.block-container {
    max-width: 1050px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* Header */

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 4px;
}

.brand-icon {
    font-size: 2.2rem;
}

.brand-title {
    font-size: 1.75rem;
    font-weight: 800;
    letter-spacing: -0.03em;
}

.brand-subtitle {
    color: #8f98a8;
    font-size: 0.92rem;
    margin-left: 3.6rem;
    margin-bottom: 1.6rem;
}

/* Memory */

.memory {
    border: 1px solid #2b3442;
    background: linear-gradient(135deg, #151a22, #11151c);
    border-radius: 16px;
    padding: 16px 18px;
    margin-bottom: 1.8rem;
    box-shadow: 0 8px 30px rgba(0,0,0,.18);
}

.memory-row {
    display: flex;
    align-items: center;
    gap: 9px;
    font-weight: 700;
}

.memory-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #45d483;
    box-shadow: 0 0 10px rgba(69,212,131,.65);
}

.memory-text {
    color: #8f98a8;
    font-size: .86rem;
    margin-top: 6px;
    line-height: 1.5;
}

/* Welcome */

.welcome {
    text-align: center;
    padding: 2rem 1rem 1rem;
}

.welcome-icon {
    font-size: 3.5rem;
    margin-bottom: .4rem;
}

.welcome-title {
    font-size: 1.7rem;
    font-weight: 750;
}

.welcome-text {
    color: #9299a6;
    max-width: 650px;
    margin: .5rem auto 1.5rem;
    line-height: 1.6;
}

/* Example cards */

.example-title {
    color: #777f8d;
    font-size: .76rem;
    font-weight: 700;
    letter-spacing: .08em;
    margin-bottom: .5rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #0b0e13;
    border-right: 1px solid #202630;
}

.sidebar-title {
    font-size: 1.15rem;
    font-weight: 800;
}

.sidebar-subtitle {
    color: #747d8c;
    font-size: .82rem;
    margin-bottom: 1rem;
}

/* Buttons */

.stButton > button {
    border-radius: 11px;
    border: 1px solid #2a303b;
    transition: all .15s ease;
}

.stButton > button:hover {
    border-color: #596579;
    transform: translateY(-1px);
}

/* Chat */

[data-testid="stChatMessage"] {
    border-radius: 16px;
    padding: 8px 12px;
    margin-bottom: 10px;
}

[data-testid="stChatInput"] {
    border-radius: 16px;
}

/* Footer */

.footer {
    text-align: center;
    color: #59616f;
    font-size: .72rem;
    margin-top: 1.5rem;
}

/* Mobile */

@media (max-width: 700px) {

    .block-container {
        padding-top: 1.2rem;
        padding-left: .8rem;
        padding-right: .8rem;
    }

    .brand-title {
        font-size: 1.45rem;
    }

    .brand-subtitle {
        margin-left: 0;
        font-size: .84rem;
    }

    .memory {
        padding: 13px 14px;
    }

    .welcome {
        padding-top: 1rem;
    }

    .welcome-title {
        font-size: 1.35rem;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================
# Sidebar
# =========================

with st.sidebar:

    st.markdown(
        '<div class="sidebar-title">🛡️ Bug Bounty Triage</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sidebar-subtitle">AI security analysis with memory</div>',
        unsafe_allow_html=True
    )

    if st.button("＋  New finding", use_container_width=True):
        create_new_conversation()
        st.rerun()

    st.divider()

    st.markdown("##### 💬 Recent findings")

    conversations = sorted(
        st.session_state.conversations,
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )

    for conversation in conversations:

        title = conversation.get("title", "New finding")

        if len(title) > 34:
            title = title[:34] + "..."

        if conversation["id"] == st.session_state.active_id:
            label = "🟢  " + title
        else:
            label = "💬  " + title

        if st.button(
            label,
            key="chat_" + conversation["id"],
            use_container_width=True
        ):
            st.session_state.active_id = conversation["id"]
            st.rerun()

    st.divider()

    st.caption("🧠 Hindsight memory")
    st.caption(
        "Long-term vulnerability knowledge is stored separately "
        "from your visible chat history."
    )


# =========================
# Main
# =========================

conversation = get_active_conversation()

st.markdown("""
<div class="brand">
    <div class="brand-icon">🛡️</div>
    <div class="brand-title">Bug Bounty Triage Agent</div>
</div>

<div class="brand-subtitle">
    AI-powered vulnerability triage that learns from previous findings.
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="memory">

<div class="memory-row">
    <span class="memory-dot"></span>
    🧠 Hindsight Memory Active
</div>

<div class="memory-text">
    Previous findings are checked for duplicates, patterns,
    regressions, and related triage decisions.
</div>

</div>
""", unsafe_allow_html=True)


# =========================
# Empty/welcome state
# =========================

user_messages = [
    m for m in conversation["messages"]
    if m["role"] == "user"
]

if not user_messages:

    st.markdown("""
    <div class="welcome">

        <div class="welcome-icon">🔎</div>

        <div class="welcome-title">
            What vulnerability are you investigating?
        </div>

        <div class="welcome-text">
            Describe your finding naturally. The agent will analyze it
            and use Hindsight to compare it with previous security findings.
        </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="example-title">TRY AN EXAMPLE</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔐  IDOR / Access Control",
            use_container_width=True
        ):
            st.session_state.example_prompt = (
                "I found an IDOR on /api/v1/users/1024 "
                "that allows unauthorized profile modification."
            )
            st.rerun()

    with col2:
        if st.button(
            "💻  Stored XSS",
            use_container_width=True
        ):
            st.session_state.example_prompt = (
                "I found a stored XSS vulnerability in the user profile "
                "bio field that executes JavaScript for other users."
            )
            st.rerun()


# =========================
# Messages
# =========================

for message in conversation["messages"]:

    with st.chat_message(message["role"]):

        if message["role"] == "assistant":
            st.markdown("**🛡️ Triage Agent**")

        st.markdown(message["content"])


# =========================
# Example prompt handling
# =========================

prompt = st.chat_input(
    "Describe a vulnerability..."
)

if "example_prompt" in st.session_state:
    prompt = st.session_state.pop("example_prompt")


# =========================
# Process finding
# =========================

if prompt:

    prompt = prompt.strip()

    if prompt:

        conversation["messages"].append({
            "role": "user",
            "content": prompt
        })

        if conversation["title"] == "New finding":
            conversation["title"] = prompt[:55]
            if len(prompt) > 55:
                conversation["title"] += "..."

        conversation["updated_at"] = datetime.now().isoformat()

        save_conversations(
            st.session_state.conversations
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            st.markdown("**🛡️ Triage Agent**")

            with st.spinner(
                "🧠 Searching Hindsight memory and analyzing finding..."
            ):

                try:

                    result = triage_vulnerability(prompt)

                    st.markdown(result)

                    conversation["messages"].append({
                        "role": "assistant",
                        "content": result
                    })

                    conversation["updated_at"] = datetime.now().isoformat()

                    save_conversations(
                        st.session_state.conversations
                    )

                except Exception as e:

                    error_message = (
                        "⚠️ The AI service is temporarily unavailable. "
                        "Please try again in a moment."
                    )

                    st.error(error_message)

                    conversation["messages"].append({
                        "role": "assistant",
                        "content": error_message
                    })

                    conversation["updated_at"] = datetime.now().isoformat()

                    save_conversations(
                        st.session_state.conversations
                    )


st.markdown(
    '<div class="footer">🔗 OpenRouter · 🧠 Hindsight · 🔒 API keys stay server-side</div>',
    unsafe_allow_html=True
)
