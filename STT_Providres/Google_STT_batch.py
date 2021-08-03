from google.cloud import speech
from google.oauth2 import service_account
import io
import os


def transcript_Google(audio_file_path, flac_file='Google.flac'):

    credentials = service_account.Credentials.from_service_account_file('D:\\PROJECT_SPRING\\SPRING\\CredentialsKeys\\Google_key.json')
    # Instantiates a client
    client = speech.SpeechClient(credentials=credentials)
    try:
        os.remove(flac_file)
    except: pass

    cmd = f'ffmpeg -i {audio_file_path} {flac_file}'
    os.system(cmd)

    with io.open(flac_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    transcript = ''
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        transcript = result.alternatives[0].transcript + ' '

    return transcript + '\n'