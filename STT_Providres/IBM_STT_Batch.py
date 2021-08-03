from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json


# the path of the audio file
audio_file_path = 'C:/Users/Amit/Dropbox/Amit_and_Pini/ASR/ASR_DOCS/test_audio.wav'

# import the credentials from the json file
with open('C:/Users/Amit/Documents/ASR_keys/IBM_key.json') as json_file:
    creds = json.load(json_file)

# instantiate the authenticator
authenticator = IAMAuthenticator(apikey=creds['apikey'])

# instantiate the recognizer with the authenticator
speech_to_text = SpeechToTextV1(
   authenticator=authenticator
)

# set the api url
speech_to_text.set_service_url('https://stream.watsonplatform.net/speech-to-text/api')

# open the audio file
audio_file = open(audio_file_path, 'rb')

# recognize the audio file with the recognizer and get the result
speech_recognition_results = speech_to_text.recognize(
    audio=audio_file,
    word_confidence=True,
    max_alternatives=3,
    timestamps=True,
).get_result()

# print the result
print(speech_recognition_results)




