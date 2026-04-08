# 🎓 MakerGhat Classroom Analytics

An AI-powered, offline-first classroom analytics prototype designed for **MakerGhat**. This system processes Hinglish audio recordings from classrooms to transcribe speech, identify interactions, and calculate teacher/student engagement metrics.

### 🔗 **[LIVE DEMO DASHBOARD](https://makerghat-jp5xwzekmexwkp9oua4cz3.streamlit.app/)**

> [!IMPORTANT]
> **Demo Performance Note:** Due to compute constraints and to ensure fast demo performance, transcription and analytics are pre-processed locally. The deployed app serves these precomputed insights.

## 🚀 Overview

This MVP provides an automated "Feedback Loop" for educators by transforming raw classroom audio into actionable visual insights.

---

## 📖 Project Documentation

### **1. My Approach**
I utilized a **Hierarchical Batch Processing** pipeline to ensure data privacy and accuracy:
1.  **Audio Ingestion**: Raw MP3 files are loaded from the `audio/` directory.
2.  **Transcription & VAD**: I use `faster-whisper` (Medium model) with a Voice Activity Detection (VAD) filter. This ensures we only process segments with actual speech.
3.  **Hinglish Context**: I inject an `initial_prompt` into the model to bias it toward mixed Hindi and English speech patterns, ensuring accurate transcription of technical terms used in MakerGhat sessions.
4.  **Hybrid Cleaning**: The raw output is passed through a custom filtering engine that removes "Ghost Segments" (long durations with very few words) caused by ambient classroom noise.
5.  **Analytics Layer**: Cleaned segments are parsed to calculate pedagogical metrics.
6.  **Visualization**: Results are served via a Streamlit Dashboard for end-user interaction.

### **2. How I Calculated Metrics**
Metrics are calculated using the `scripts/calculate_metrics.py` logic:
-   **Teacher Dominance Ratio**: Calculated as `(Total Teacher Talk Duration / Total Clean Audio Duration) * 100`. This measures the percentage of time the teacher is speaking.
-   **Student Participation Indicator**: Calculated as `(Number of Student Utterances / Total Segment Count) * 100`. This tracks how frequently students are speaking up, regardless of duration.
-   **Interaction Switches**: A switch is counted every time the speaker changes from Teacher to Student or vice-versa. A high count indicates high engagement.
-   **Teacher Questions**: Detected using a heuristic keyword search (`kya`, `kyu`, `kaise`, etc.) and punctuation analysis.
-   **Transcription Density (Quality Flag)**: Calculated as `Words Per Minute (WPM)`. If WPM < 5, the session is flagged as "Incomplete Data."

### **3. Tools & Models Used**
-   **Transcription**: `faster-whisper` (Medium Model) for high-speed, local inference.
-   **Frontend**: `Streamlit` for a clean, interactive dashboard.
-   **Visualizations**: `Plotly` for dynamic talk-time and health charts.
-   **Data Management**: `Pandas` for efficient processing of large transcription datasets.
-   **Acceleration**: `CUDA` (NVIDIA) for 3x real-time processing speeds.

### **4. Assumptions**
- **Speaker Mapping**: The model assumes the dominant voice in teacher-led sessions is the "Teacher" and others are "Students."
- **Language**: I assume the classroom environment is primarily Hinglish (Hindi + English).
- **Silence Baseline**: I assume that any continuous segment longer than 60 seconds with fewer than 5 words represents background noise or a break in the session, rather than meaningful dialogue.

### **5. Limitations**
- **Overlapping Speech**: The current pipeline may struggle to accurately attribute speech during "Crosstalk" (multiple people speaking at once).
- **Heuristic Diarization**: I use a heuristic start-time clustering for speaker labels rather than biometric voice fingerprints.
- **Compute Heavy**: Reprocessing the raw audio requires a local NVIDIA GPU; the web-app is read-only for precomputed data.

---

## 🛠️ Full Pipeline Reproduction (Optional)

If you wish to run the **transcription** and **metrics analysis** yourself (requires a high-end local GPU), follow these additional steps:

### **1. Download Assets**
Due to size constraints, the raw audio and AI model weights are hosted separately:
- **[DOWNLOAD AUDIO (Google Drive)]**: https://drive.google.com/drive/folders/1_WNSZFva4XPiRHlKxrhpUkrih5MiPk0D?usp=sharing
- **[DOWNLOAD MODELS (Google Drive)]**: https://drive.google.com/file/d/1iXjkiJpXJSqX9rluintmmkY0y67aOLyi/view?usp=drive_link
### **2. Setup Directories**
Place the extracted folders in the project root:
```text
/makerghat-classroom-analytics
├── audio/          <-- Place raw .mp3 files here
├── models/         <-- Place whisper-medium folder here
└── processed_data/
```

### **3. Dependency Strategy**
| File | Purpose | Usage |
| :--- | :--- | :--- |
| **`requirements.txt`** | **Production (Web)** | Lightweight libs for Cloud Dashboard only. |
| **`requirements-dev.txt`** | **Full Suite (Local)** | AI Muscles + Dashboard + Development tools. |

### **4. Run Analysis**
```powershell
pip install -r requirements-dev.txt
& ".\.venv\Scripts\python.exe" scripts/fix_dlls.py
& ".\.venv\Scripts\python.exe" scripts/process_audio.py
& ".\.venv\Scripts\python.exe" scripts/calculate_metrics.py
```

---

## 📦 Dashboard Setup (Local)
```powershell
git clone https://github.com/LIKITH-S/classroom.git
cd classroom
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

---


Developed as a technical prototype for **MakerGhat Classroom Analytics**. 