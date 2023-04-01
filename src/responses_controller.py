import os
import openai
from pytube import YouTube


# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")
OUTPUT_PATH = "../data"


def get_response(input: str) -> str:
    return "Use `/help` command for help"


def get_audio_transcription(url: str, language: str) -> str:

    # Create a YouTube object from the URL
    yt_video = YouTube(url)

    # Get the audio stream
    audio_stream = yt_video.streams.filter(only_audio=True).first()

    # Download the audio stream
    output_path = "data"
    filename = f"{yt_video.title}.mp3"
    audio_stream.download(output_path=output_path, filename=filename)

    with open(f"{output_path}/{filename}", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, language=language) if language else\
            openai.Audio.transcribe("whisper-1", audio_file)

    return transcript.text