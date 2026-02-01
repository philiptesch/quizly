import json
import yt_dlp
import whisper
from google import genai
import secrets
from glob import glob
from pathlib import Path

def check_video(url: str):
    """
    Check whether a given video URL is valid and accessible.

    Args:
        url (str): Video URL to be checked.

    Returns:
        bool:
            - True if the video exists and metadata can be extracted.
            - False if the video is unavailable or invalid.
    """
    try:
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return True
    except yt_dlp.utils.DownloadError:
        return False


def video_download(url: str):
    """
    Download the audio stream from a video URL.

    Behavior:
        - Validates the video URL before downloading.
        - Downloads the best available audio format.
        - Stores the audio file in the media directory.

    Args:
        url (str): Video URL.

    Returns:
        str | bool:
            - Path to the downloaded audio file on success.
            - False if validation or download fails.
    """
    udid = secrets.randbelow(1000) + 1
    
    audio_data = f"media/audio_{udid}."
    URL = url
    if check_video(url):
        ydl_opts = {"format": "bestaudio/best","outtmpl": f"{audio_data}%(ext)s","quiet": False,"noplaylist": True, 
                    "cookiefile": "cookies.txt",
                "extractor_args": {
                "youtube": {
                "player_client": ["default,-android_sdkless"]
            }
        },}
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
    """
    Transcribe an audio file into text using OpenAI Whisper.

    Args:
        audio (str): Path to the audio file.

    Returns:
        str: Transcribed text extracted from the audio.
    """

    model = whisper.load_model("base")
    audio_path = str(Path(audio))
    result = model.transcribe(audio_path)
    return result["text"]



def promted_Text():
    """
    Generate the prompt instructions for the AI quiz generator.

    Behavior:
        - Defines the exact JSON structure required for quiz creation.
        - Enforces strict rules for number of questions and answers.

    Returns:
        str: Prompt text sent to the AI model.
    """

    return """
The quiz must follow this exact structure:

{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
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
    """
    Generate a quiz from a transcript using the Gemini AI API.

    Behavior:
        - Sends transcript text with strict prompt instructions.
        - Receives AI-generated quiz data in JSON format.
        - Parses and returns the JSON as a Python dictionary.

    Args:
        transcript (str): Transcribed text from the video audio.

    Returns:
        dict: Parsed quiz data including title, description, and questions.

    Raises:
        json.JSONDecodeError: If the AI response is not valid JSON.
    """
    client = genai.Client()
    prompt_text = promted_Text()
    response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=prompt_text+transcript,)
    prompt = response.text.replace("\n", " ").strip()
    data = json.loads(prompt)
    return data
