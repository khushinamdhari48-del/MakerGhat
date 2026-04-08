import os
import sys
import site
import json

# FIX: Windows DLL search path for NVIDIA libraries installed via pip
# This must happen BEFORE importing faster_whisper or torch
if os.name == 'nt':
    # 1. Force find sympy in case of environment mixups
    try:
        import sympy
    except ImportError:
        pass
        
    # 2. Add NVIDIA DLL directories to the search path
    for site_pkg in site.getsitepackages():
        nvidia_base = os.path.join(site_pkg, 'nvidia')
        if os.path.exists(nvidia_base):
            for folder in os.listdir(nvidia_base):
                bin_path = os.path.join(nvidia_base, folder, 'bin')
                if os.path.exists(bin_path):
                    print(f"Adding DLL Directory: {bin_path}")
                    os.add_dll_directory(bin_path)

from faster_whisper import WhisperModel
from tqdm import tqdm
import pandas as pd

# CONFIGURATION
LOCAL_MODEL_PATH = "models/whisper-medium"
DEFAULT_MODEL_SIZE = "medium"
DEVICE = "cuda"         # Enabling GPU acceleration!
COMPUTE_TYPE = "float16" # Optimal for RTX 40-series GPU
AUDIO_DIR = "audio"
OUTPUT_DIR = "processed_data"
HINGLISH_PROMPT = "Students, focus! Aaj hum class mein naya topic start karenge. Do you have any questions before we begin?"

def get_speaker_label(segment_text, segment_duration, prev_label):
    """
    Very basic heuristic for Teacher vs Student labelling.
    Teacher: Long explanations, asks questions, uses pedagogical keywords.
    Student: Short responses, answers directly after a teacher question.
    """
    teacher_keywords = ["open", "chapter", "book", "homework", "listen", "class", "attention", "kitne", "kaise", "kya"]
    text_lower = segment_text.lower()
    
    # Heuristic 1: If it's a long segment (> 4s), it's likely the teacher
    if segment_duration > 4.0:
        return "Teacher"
    
    # Heuristic 2: If it contains pedagogical keywords
    if any(word in text_lower for word in teacher_keywords):
        return "Teacher"
    
    # Heuristic 3: If it ends in a question mark, likely Teacher
    if segment_text.strip().endswith('?'):
        return "Teacher"
    
    # Heuristic 4: Short response after a Teacher's segment is likely Student
    if prev_label == "Teacher" and segment_duration < 4.0:
        return "Student"
    
    # Default fallback
    return "Teacher" if segment_duration > 2.0 else "Student"

def process_audio():
    # 1. Initialize model
    # Prefer local path if it exists, otherwise fall back to name download
    model_source = LOCAL_MODEL_PATH if os.path.isdir(LOCAL_MODEL_PATH) else DEFAULT_MODEL_SIZE
    
    print(f"Loading Whisper model from: {model_source}...")
    model = WhisperModel(model_source, device=DEVICE, compute_type=COMPUTE_TYPE)
    
    # Ensure folders exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    audio_files = [f for f in os.listdir(AUDIO_DIR) if f.endswith(('.mp3', '.wav', '.m4a', '.flac'))]
    
    if not audio_files:
        print(f"No audio files found in {AUDIO_DIR}/. Please add the classroom recordings and run again.")
        return
    
    for idx, filename in enumerate(audio_files, 1):
        print(f"\n[{idx}/{len(audio_files)}] Processing: {filename}")
        audio_path = os.path.join(AUDIO_DIR, filename)
        output_path = os.path.join(OUTPUT_DIR, f"{os.path.splitext(filename)[0]}.json")
        
        # 2. Transcription
        # language='hi' helps preserve Hindi characters and Hinglish flow
        # initial_prompt guides the model towards Hinglish code-switching
        # vad_filter handles silence and low-clarity noise in 2/5 files
        segments, info = model.transcribe(
            audio_path,
            language='hi',
            initial_prompt=HINGLISH_PROMPT,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        
        results = []
        prev_label = None
        print("Transcribing segments...")
        
        for segment in segments:
            duration = segment.end - segment.start
            label = get_speaker_label(segment.text, duration, prev_label)
            
            results.append({
                "speaker_label": label,
                "start_time": round(segment.start, 2),
                "end_time": round(segment.end, 2),
                "text": segment.text.strip(),
                "confidence": round(segment.avg_logprob, 2)
            })
            prev_label = label
            print(f"  [{segment.start:.2f}s -> {segment.end:.2f}s] {label}: {segment.text.strip()}", flush=True)
            
        # 3. Final Correction (Dominance Heuristic)
        # In a real classroom, the person with the most talk time is the teacher.
        # We can recalibrate if our initial heuristic failed.
        if results:
            df = pd.DataFrame(results)
            teacher_time = df[df['speaker_label'] == "Teacher"]['text'].str.len().sum()
            student_time = df[df['speaker_label'] == "Student"]['text'].str.len().sum()
            
            # If "Students" supposedly spoke way more than the "Teacher", something is wrong.
            # We Flip if ratio is clearly inverted. (Basic safety for the MVP)
            if student_time > teacher_time * 1.5:
                for r in results:
                    r['speaker_label'] = "Student" if r['speaker_label'] == "Teacher" else "Teacher"

        # Save to JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
    print(f"\nProcessing Complete. JSON files saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    process_audio()
