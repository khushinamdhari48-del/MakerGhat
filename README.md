# 🎓 MakerGhat Classroom Analytics

An AI-powered, offline-first classroom analytics prototype designed for **MakerGhat**. This system processes Hinglish audio recordings from classrooms to transcribe speech, identify interactions, and calculate teacher/student engagement metrics.

> [!IMPORTANT]
> **Demo Performance Note:** Due to compute constraints and to ensure fast demo performance, transcription and analytics are pre-processed locally. The deployed app serves these precomputed insights.

![MakerGhat Analytics Dashboard](https://makerghat.org/wp-content/uploads/2021/04/MakerGhat-Logo-Yellow-01.png)

## 🚀 Overview

This MVP provides an automated "Feedback Loop" for educators by transforming 3+ hours of raw audio into actionable visual insights.

### **Core Features:**
- **High-Speed Transcription:** GPU-accelerated (NVIDIA RTX) Hinglish speech-to-text using `faster-whisper`.
- **Engagement Metrics:** Automatic calculation of **Teacher Dominance**, **Student Participation**, and **Interaction Frequency**.
- **Data Quality Filtering:** A hybrid heuristic engine that removes 16+ minute "ghost segments" caused by classroom noise/silence.
- **Interactive Dashboard:** A professional Streamlit UI customized with MakerGhat brand colors.

---

## 🛠️ Full Pipeline Reproduction (Optional)

If you wish to run the **transcription** and **metrics analysis** yourself (requires a high-end local GPU), follow these additional steps:

### **1. Download Assets**
Due to size constraints, the raw audio and AI model weights are hosted separately:
- **[DOWNLOAD AUDIO (Google Drive)]**: https://drive.google.com/drive/folders/1zGIuBkR0BEjoC9cx3RK4F6IfFO4gZ-8y?usp=drive_link
- **[DOWNLOAD MODELS (Google Drive)]**: https://drive.google.com/file/d/1iXjkiJpXJSqX9rluintmmkY0y67aOLyi/view?usp=drive_link
- **Contents**: `audio/` (Raw MP3s) and `models/` (Whisper Medium Weights).

### **2. Setup Directories**
Place the extracted folders in the project root:
```text
/makerghat-classroom-analytics
│   app.py
├── audio/          <-- Place raw .mp3 files here
├── models/         <-- Place whisper-medium folder here
└── processed_data/
```

### **3. Run Analysis**
```powershell
# 1. Fix DLLs (Windows only)
& ".\.venv\Scripts\python.exe" scripts/fix_dlls.py

# 2. Run Transcription (Requires GPU)
& ".\.venv\Scripts\python.exe" scripts/process_audio.py

# 3. Calculate Insights
& ".\.venv\Scripts\python.exe" scripts/calculate_metrics.py
```

---

## 📊 Technical Notes

## 📦 Installation

### **1. Prerequisites**
- Python 3.9+
- NVIDIA GPU (Recommended for speed)
- Virtual Environment (`.venv`)

### **2. Setup**
```powershell
# Clone the repository
git clone https://github.com/your-username/makerghat-classroom-analytics.git
cd makerghat-classroom-analytics

# Setup virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Run the Dashboard**
```powershell
streamlit run app.py
```

---

## 📊 Technical Notes

### **Hinglish Optimization**
The system uses a custom `initial_prompt` to bias the Whisper model toward mixed-language Hindi and English context, which is common in Indian classrooms.

### **VAD & Noise Handling**
We utilize a `vad_filter` to ignore background noise. For low-clarity sessions, we calculate **Transcription Density (words per minute)** and flag sessions below 5wpm as "Incomplete Data" to avoid misleading metrics.

---

## 👨‍💻 Developed By
Developed as a technical prototype for **MakerGhat Classroom Analytics**. 

*Powered by Antigravity AI.*
