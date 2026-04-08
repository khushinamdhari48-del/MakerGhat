import os
import json
import pandas as pd

# CONFIGURATION
PROCESSED_DATA_DIR = "processed_data"
SUMMARY_FILE = os.path.join(PROCESSED_DATA_DIR, "summary_metrics.json")

def calculate_metrics_for_file(json_path):
    """
    Calculates engagement metrics with hybrid filtering and quality flagging.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        # Check if already wrapped or not
        raw_data = json.load(f)
        data = raw_data.get("utterances", raw_data) if isinstance(raw_data, dict) else raw_data
        
    if not data:
        return None
    
    df = pd.DataFrame(data)
    df['duration'] = df['end_time'] - df['start_time']
    df['word_count'] = df['text'].str.split().str.len()
    
    # 1. Hybrid Filter for "Ghost" segments (duration > 60s AND word count < 5)
    # These distort Teacher Dominance metrics.
    mask_ghost = (df['duration'] > 60) & (df['word_count'] < 5)
    clean_df = df[~mask_ghost].copy()
    
    # 2. Density & Quality Flag
    total_words = clean_df['word_count'].sum()
    total_duration_sec = clean_df['duration'].sum()
    total_duration_min = total_duration_sec / 60 if total_duration_sec > 0 else 0
    words_per_minute = total_words / total_duration_min if total_duration_min > 0 else 0
    
    quality_status = "Incomplete Data" if words_per_minute < 5 else "Success"
    
    # 3. Core Metrics based on clean data
    total_segments = len(clean_df)
    
    # Teacher Dominance Ratio
    teacher_time = clean_df[clean_df['speaker_label'] == "Teacher"]['duration'].sum()
    teacher_dominance_ratio = (teacher_time / total_duration_sec * 100) if total_duration_sec > 0 else 0
    
    # Student Participation Indicator
    student_utterances = len(clean_df[clean_df['speaker_label'] == "Student"])
    student_participation_indicator = (student_utterances / total_segments * 100) if total_segments > 0 else 0
    
    # Interaction Count (Back-and-forth)
    interaction_count = 0
    if total_segments > 1:
        labels = clean_df['speaker_label'].tolist()
        for i in range(1, total_segments):
            if labels[i] != labels[i-1]:
                interaction_count += 1
                
    # Questions Asked (Teacher specific)
    question_keywords = ["kya", "kyu", "kaise", "kitne", "kahin", "kaun"]
    teacher_df = clean_df[clean_df['speaker_label'] == "Teacher"]
    
    questions_count = 0
    for _, row in teacher_df.iterrows():
        text = row['text'].lower().strip()
        if text.endswith('?') or any(kw in text for kw in question_keywords):
            questions_count += 1
            
    # Metrics metadata
    metrics = {
        "filename": os.path.basename(json_path),
        "quality_status": quality_status,
        "transcription_density_wpm": round(words_per_minute, 2),
        "total_segments": total_segments,
        "total_duration_sec": round(total_duration_sec, 2),
        "teacher_dominance_ratio": round(teacher_dominance_ratio, 2),
        "student_participation_indicator": round(student_participation_indicator, 2),
        "interaction_count": interaction_count,
        "questions_asked": questions_count
    }
    
    return metrics, data

def run_analysis():
    print("Starting Optimized Phase 2: Engagement Insights...")
    
    if not os.path.exists(PROCESSED_DATA_DIR):
        print(f"Error: {PROCESSED_DATA_DIR} directory not found.")
        return
        
    json_files = [f for f in os.listdir(PROCESSED_DATA_DIR) if f.endswith('.json') and f != "summary_metrics.json"]
    
    all_summary = []
    
    for filename in json_files:
        json_path = os.path.join(PROCESSED_DATA_DIR, filename)
        result = calculate_metrics_for_file(json_path)
        
        if result:
            metrics, original_utterances = result
            print(f"[{metrics['quality_status']}] {filename}: Density: {metrics['transcription_density_wpm']} wpm | Dominance: {metrics['teacher_dominance_ratio']}%")
            
            # Per-Class detailed report update
            updated_data = {
                "metadata": metrics,
                "utterances": original_utterances
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            
            all_summary.append(metrics)
                
    # Save a global summary for the dashboard initial load
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)
        
    print(f"\nFinalized Metrics saved to individual files and {SUMMARY_FILE}")

if __name__ == "__main__":
    run_analysis()

if __name__ == "__main__":
    run_analysis()
