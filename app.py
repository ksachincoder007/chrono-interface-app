# First, ensure you have the necessary libraries installed:
# pip install streamlit wikipedia reportlab google-generativeai

import streamlit as st
import wikipedia
import time
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
import google.generativeai as genai

# --- Page Configuration ---
st.set_page_config(
    page_title="ChronoPedia Interface",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- API Configuration ---
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_CONFIGURED = True
except (KeyError, AttributeError):
    GEMINI_CONFIGURED = False

# --- THE AETHERIS UI/UX ENGINE ---
def load_css():
    """
    This injects the complete, super-enhanced CSS.
    Every detail is crafted for a futuristic, tactile, and immersive experience.
    """
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Share+Tech+Mono&display=swap');
            
            /* PRINCIPLE 1: SENTIENT ENVIRONMENT */
            @keyframes gradient-breathing {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }
            @keyframes scanline {
                0% { top: -10%; }
                100% { top: 110%; }
            }
            .stApp {
                background: linear-gradient(-45deg, #020024, #090979, #00284d, #020024);
                background-size: 400% 400%;
                animation: gradient-breathing 25s ease infinite;
                font-family: 'Orbitron', sans-serif;
            }

            /* --- HOLOGRAPHIC PANELS with Scanline Effect --- */
            [data-testid="column"], [data-testid="stSidebar"] {
                background: rgba(10, 10, 30, 0.7);
                backdrop-filter: blur(20px) saturate(180%);
                border: 1px solid rgba(0, 255, 255, 0.25);
                border-radius: 1rem;
                padding: 1.5rem;
                margin-top: 1rem;
                box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
                position: relative;
                overflow: hidden; /* Crucial for scanline effect */
            }
            [data-testid="column"]::after { /* Scanline effect */
                content: '';
                position: absolute;
                left: 0;
                width: 100%;
                height: 2px;
                background: rgba(0, 255, 255, 0.3);
                box-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
                animation: scanline 8s linear infinite;
            }

            /* --- VISUAL HIERARCHY & TYPOGRAPHY --- */
            h1, h2, h3 {
                color: #00ffff;
                text-shadow: 0 0 4px #00ffff, 0 0 8px #00ffff;
                font-weight: 700;
                text-align: center;
            }
            p, div, li, span, small {
                font-family: 'Share Tech Mono', monospace;
                color: #e0e6f0; /* Softer, more readable white */
                line-height: 1.7;
            }

            /* PRINCIPLE 2: TACTILE & RESPONSIVE FEEDBACK */
            /* --- THE ULTIMATE FLOATING BUTTON --- */
            .stButton > button {
                width: 100%;
                border: 1px solid #00ffff;
                background: linear-gradient(45deg, rgba(0, 255, 255, 0.1), rgba(0, 255, 255, 0.2));
                color: #00ffff;
                font-family: 'Orbitron', sans-serif;
                font-weight: 700;
                transition: transform 0.3s ease, box-shadow 0.3s ease, color 0.3s ease;
                position: relative;
                overflow: hidden; /* For liquid shimmer */
            }
            .stButton > button:hover {
                transform: translateY(-7px) scale(1.03); /* Enhanced float */
                box-shadow: 0 10px 30px rgba(0, 255, 255, 0.35);
                color: white;
            }
            .stButton > button:active {
                transform: translateY(0px) scale(1);
                box-shadow: 0 0 5px #00ffff, 0 0 10px #00ffff inset;
            }
            /* Liquid shimmer effect on hover */
            .stButton > button::before {
                content: '';
                position: absolute;
                top: 0; left: -150%; width: 100%; height: 100%;
                background: linear-gradient(to right, transparent 0%, rgba(255,255,255,0.3) 50%, transparent 100%);
                transition: left 0.8s ease;
                transform: skewX(-25deg);
            }
            .stButton > button:hover::before {
                left: 150%;
            }
            
            /* --- FUTURISTIC CHAT INTERFACE --- */
            .chat-message {
                padding: 1rem 1.25rem;
                border-radius: 0.75rem;
                margin-bottom: 0.75rem;
                border-width: 1px;
                border-style: solid;
                transition: all 0.3s ease;
            }
            .user-message {
                background-color: rgba(80, 130, 255, 0.15);
                border-color: rgba(80, 130, 255, 0.4);
                border-left-width: 5px;
            }
            .assistant-message {
                background-color: rgba(0, 255, 255, 0.1);
                border-color: rgba(0, 255, 255, 0.3);
                border-left-width: 5px;
            }
            .stChatInput {
                 background-color: transparent;
            }

            /* PRINCIPLE 3: VISUAL COHESION */
            /* --- UNIFIED SIDEBAR --- */
            [data-testid="stSidebar"] {
                padding: 1rem;
            }
            [data-testid="stSidebar"]::after {
                 animation-duration: 12s; /* Slower scanline for sidebar */
            }

            /* --- EXTREME RESPONSIVENESS --- */
            @media (max-width: 768px) {
                [data-testid="column"] {
                    margin-bottom: 1rem; /* Space between stacked columns */
                }
            }
        </style>
    """, unsafe_allow_html=True)

# --- PDF Generation Function (No changes needed) ---
def create_pdf(title, summary, url):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='TitleStyle', parent=styles['h1'], fontName='Helvetica-Bold', fontSize=24, alignment=TA_CENTER, spaceAfter=24)
    summary_style = ParagraphStyle(name='SummaryStyle', parent=styles['BodyText'], fontName='Helvetica', fontSize=12, leading=18)
    url_style = ParagraphStyle(name='URLStyle', parent=styles['Italic'], fontName='Helvetica-Oblique', fontSize=10, textColor='blue', spaceBefore=20)
    story = [Paragraph(title, title_style), Paragraph(summary.replace('\n', '<br/>'), summary_style), Spacer(1, 24), Paragraph(f"Source: <a href='{url}'>{url}</a>", url_style)]
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Gemini Chatbot Function (No changes needed) ---
def get_gemini_response(prompt):
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt, stream=True)
    return response

# --- Initialize Session State ---
if 'search_topic' not in st.session_state:
    st.session_state.search_topic = ""
if 'last_article' not in st.session_state:
    st.session_state.last_article = None
if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Render the UI ---
load_css()

# --- Sidebar for PDF Export ---
with st.sidebar:
    st.markdown("<h2>Chrono-Exporter</h2>", unsafe_allow_html=True)
    if st.session_state.last_article:
        if st.button("Generate PDF Report", key="generate_pdf"):
            with st.spinner("Compiling data..."):
                article = st.session_state.last_article
                pdf = create_pdf(article['title'], article['summary'], article['url'])
                st.session_state.pdf_buffer = pdf
        if st.session_state.pdf_buffer:
            st.download_button(label="Download Report", data=st.session_state.pdf_buffer, file_name=f"{st.session_state.last_article['title'].replace(' ', '_')}_Report.pdf", mime="application/pdf")
    else:
        st.info("Retrieve an article to enable PDF export.")

# --- Main Two-Column Layout ---
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    st.header("ChronoPedia Search")
    search_input = st.text_input("Enter your query:", placeholder="e.g., General Relativity, CRISPR...", label_visibility="collapsed")
    if st.button("Initiate Search"):
        st.session_state.search_topic = search_input
        st.session_state.last_article = None
        st.session_state.pdf_buffer = None
        st.session_state.chat_history = []
        st.rerun()

    if st.session_state.search_topic and not st.session_state.last_article:
        with st.spinner(f"Querying archives for '{st.session_state.search_topic}'..."):
            try:
                page = wikipedia.page(st.session_state.search_topic, auto_suggest=True, redirect=True)
                st.session_state.last_article = {"title": page.title, "summary": page.summary, "url": page.url}
                st.rerun()
            except wikipedia.exceptions.DisambiguationError as e:
                st.warning("Ambiguity Detected. Refine your search:")
                for option in e.options[:5]:
                    if st.button(option, key=f"option_{option}"):
                        st.session_state.search_topic = option
                        st.rerun()
            except Exception:
                st.error(f"Archive Error: No data found for query '{st.session_state.search_topic}'.")

    if st.session_state.last_article:
        article = st.session_state.last_article
        st.subheader(f"Data Stream: {article['title']}")
        st.success("Summary:")
        st.write(article['summary'])
        st.info(f"Full data archive available at: [Access Link]({article['url']})")
    else:
        st.info("Awaiting your query to access the knowledge archives.")

with col2:
    st.header("AI Assistant")
    if not GEMINI_CONFIGURED:
        st.error("Gemini API key not configured. Please add it to your `.streamlit/secrets.toml` file.")
    else:
        # Chat history container
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.chat_history:
                role_class = "user-message" if message["role"] == "user" else "assistant-message"
                with st.markdown(f'<div class="chat-message {role_class}">', unsafe_allow_html=True):
                    st.markdown(f'**{message["role"].capitalize()}:** {message["text"]}')
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input at the bottom
        ai_placeholder = f"Ask about '{st.session_state.last_article['title']}'..." if st.session_state.last_article else "Ask me anything..."
        if prompt := st.chat_input(ai_placeholder):
            st.session_state.chat_history.append({"role": "user", "text": prompt})
            final_prompt = prompt
            if st.session_state.last_article:
                article = st.session_state.last_article
                final_prompt = f"Based on this article summary about '{article['title']}': '{article['summary']}', answer the user's question: '{prompt}'"
            
            with st.chat_message("assistant"):
                response_stream = get_gemini_response(final_prompt)
                response_container = st.empty()
                full_response = ""
                for chunk in response_stream:
                    full_response += chunk.text
                    response_container.markdown(full_response + "▌")
                response_container.markdown(full_response)
                st.session_state.chat_history.append({"role": "assistant", "text": full_response})
                st.rerun()