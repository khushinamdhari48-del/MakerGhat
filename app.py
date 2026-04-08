import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="MakerGhat | Classroom Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- BRANDING & STYLING ---
MAKERGHAT_GREEN = "#00A859"
MAKERGHAT_YELLOW = "#FFD200"
MAKERGHAT_DARK = "#1E1E1E"

st.markdown(f"""
    <style>
    .main {{
        background-color: {MAKERGHAT_DARK};
    }}
    .stMetric {{
        background-color: #2D2D2D;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid {MAKERGHAT_GREEN};
    }}
    .stBadge {{
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
    }}
    .status-incomplete {{
        background-color: #FF4B4B;
        color: white;
    }}
    .status-success {{
        background-color: {MAKERGHAT_GREEN};
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

# --- DATA HELPERS ---
PROCESSED_DIR = "processed_data"
SUMMARY_FILE = os.path.join(PROCESSED_DIR, "summary_metrics.json")

@st.cache_data
def load_summary():
    if os.path.exists(SUMMARY_FILE):
        with open(SUMMARY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@st.cache_data
def load_class_data(filename):
    path = os.path.join(PROCESSED_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

# --- SIDEBAR ---
st.sidebar.image("https://makerghat.org/wp-content/uploads/2021/04/MakerGhat-Logo-Yellow-01.png", width=200) # Fallback logo
st.sidebar.title("📊 Control Panel")

summary_data = load_summary()
if not summary_data:
    st.error("No processed data found. Please run scripts/process_audio.py and scripts/calculate_metrics.py first.")
    st.stop()

# Class selection
filenames = [item['filename'] for item in summary_data]
selected_filename = st.sidebar.selectbox("Select Classroom Session", filenames)

selected_metrics = next(item for item in summary_data if item['filename'] == selected_filename)

# Quality Banner
st.sidebar.markdown("---")
if selected_metrics['quality_status'] == "Incomplete Data":
    st.sidebar.error("⚠️ Quality: Incomplete Data")
    st.sidebar.caption("This session has low transcription density, likely due to background noise.")
else:
    st.sidebar.success("✅ Quality: High Clarity")

# --- MAIN DASHBOARD ---
st.title(f"🏫 Classroom Insights: {selected_filename}")
st.caption("AI-Powered Hinglish Analytics Prototype for MakerGhat")

# Row 1: High Level Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Teacher Dominance", f"{selected_metrics['teacher_dominance_ratio']}%")
with m2:
    st.metric("Interaction Switches", selected_metrics['interaction_count'])
with m3:
    st.metric("Student Voices", f"{selected_metrics['student_participation_indicator']}%")
with m4:
    st.metric("Teacher Questions", selected_metrics['questions_asked'])

st.divider()

# Row 2: Visualizations
c1, c2 = st.columns([1, 1])

# Pie Chart for Talk Distribution
with c1:
    st.subheader("Talk Time Distribution")
    pie_data = pd.DataFrame({
        "Speaker": ["Teacher", "Students"],
        "Value": [selected_metrics['teacher_dominance_ratio'], 100 - selected_metrics['teacher_dominance_ratio']]
    })
    fig_pie = px.pie(
        pie_data, 
        values='Value', 
        names='Speaker',
        color_discrete_sequence=[MAKERGHAT_GREEN, MAKERGHAT_YELLOW],
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# Transcription Density
with c2:
    st.subheader("Session Health")
    st.write(f"**Transcription Density:** {selected_metrics['transcription_density_wpm']} words per minute")
    progress = min(selected_metrics['transcription_density_wpm'] / 100, 1.0)
    st.progress(progress)
    st.caption("Optimal classroom density is 40-100 wpm. Lower values indicate muffled audio or silence.")

st.divider()

# Row 3: Transcript Viewer
st.subheader("👨‍🏫 Dynamic Transcript (Hin-glish)")

full_data = load_class_data(selected_filename)
if full_data and "utterances" in full_data:
    utterances = full_data["utterances"]
    
    # Filter controls
    f1, f2 = st.columns([2, 1])
    search_q = f1.text_input("🔍 Search transcript...", "")
    speaker_filter = f2.multiselect("Filter Speaker", ["Teacher", "Student"], default=["Teacher", "Student"])
    
    for u in utterances:
        # Filtering logic
        if u['speaker_label'] not in speaker_filter:
            continue
        if search_q.lower() not in u['text'].lower():
            continue
            
        # UI Bubble
        with st.chat_message("user" if u['speaker_label'] == "Teacher" else "assistant", 
                             avatar="👨‍🏫" if u['speaker_label'] == "Teacher" else "🧑‍🎓"):
            st.write(f"**{u['speaker_label']}** | {u['start_time']}s - {u['end_time']}s")
            st.write(u['text'])
else:
    st.info("Transcript utterances not found in this file.")

st.sidebar.markdown("---")
st.sidebar.info("Prototype developed by Antigravity AI.")
