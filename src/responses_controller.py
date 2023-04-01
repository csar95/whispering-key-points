import os
import openai
from pytube import YouTube


# Load your API key from an environment variable or secret management service
openai.api_key = os.getenv("OPENAI_API_KEY")
OUTPUT_PATH = "../data"


def get_response(input: str) -> str:
    return "Use `/help` command for help"


def get_chatGPT_response(url: str, language: str, prompt: str, model: str) -> str:

    # Create a YouTube object from the URL
    yt_video = YouTube(url)

    # Get the audio stream
    audio_stream = yt_video.streams.filter(only_audio=True).first()

    # Download the audio stream
    output_path = "data"
    filename = f"{yt_video.title}.mp3"
    audio_stream.download(output_path=output_path, filename=filename)

    # Get transcript of the YouTube video's audio
    with open(f"{output_path}/{filename}", "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file, language=language) if language else\
            openai.Audio.transcribe("whisper-1", audio_file)

    # Send the transcript along with the user's prompt to ChatGPT
    res = openai.ChatCompletion.create(model=model,
                                       messages=[{
                                           "role": "system",
                                           "content": "You are ChatGPT, a large language model trained by OpenAI. Answer as concisely as possible."
                                       },
                                       {
                                           "role": "user",
                                           "content": f"{prompt} {transcript.text}"
                                       }])

    return res['choices'][0]['message']['content']