import json
import yt_dlp
import whisper
from google import genai
import secrets
from glob import glob
from pathlib import Path

def check_video(url: str):
    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return True
    except yt_dlp.utils.DownloadError:
        return False


def video_download(url: str):
    udid = secrets.randbelow(100) + 1
    
    audio_data = f"media/audio_{udid}."
    URL = url
    if check_video(url):
        ydl_opts = {"format": "bestaudio/best","outtmpl": f"{audio_data}%(ext)s","quiet": False,"noplaylist": True,}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            error_code = ydl.download([URL])    
            audio_files = glob(f"{audio_data}*")
            if error_code is None or error_code == 0 :
                return audio_files[0]
            else:
                 return False
    else:
        return False


def transcripts_Audio_to_Text(audio:str):

    model = whisper.load_model("base")
    audio_path = str(Path(audio))
    result = model.transcribe(audio_path)
    return result["text"]



def promted_Text():
    return """
The quiz must follow this exact structure:

{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above question_options like Option A and no exact text"
    }
  ]
}

Requirements:
- exactly 10 questions
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question.
- The output must be valid JSON.
- No explanations, no code fences.
""" 

def create_Quiz_with_GeminiAPI(transcript):
        client = genai.Client()
        prompt_text = promted_Text()
        response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt_text+transcript,)
        print(response.text)
        prompt = response.text.replace("\n", " ").strip()
        data = json.loads(prompt)
        return data
