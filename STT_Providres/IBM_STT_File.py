from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def transcript_IBM(audio_file_path):
    # authenticator = IAMAuthenticator(apikey='c_v5jYX0K-5Idrv1MxGknOgBmm-odWJ5lTCxLdh89ZfG')
    authenticator = IAMAuthenticator(apikey='meSBzgaix1rLcNfJ0X4e1F-aG8A6LBxjvHK2yTLIZUS_')
    speech_to_text = SpeechToTextV1(
        authenticator=authenticator
    )
    speech_to_text.set_service_url(
        'https://api.eu-gb.speech-to-text.watson.cloud.ibm.com/instances/e2f5f44f-8bf6-4058-a8be-5c8628ac88d2')

    audio_file = open(audio_file_path, 'rb')

    speech_recognition_results = speech_to_text.recognize(
        audio=audio_file,
        model='fr-FR_BroadbandModel'
    ).get_result()

    try:
        result = speech_recognition_results['results'][0]['alternatives'][0]['transcript'] + '\n'
    except:
        result = '\n'

    return result


def transcribe_file(wav_scp_file, out_file):
    wav_scp = open(wav_scp_file, 'r')
    lines = wav_scp.readlines()

    paths = []
    for line in lines:
        _, path = line.split(' ')
        paths.append(path[:-1])

    wav_scp.close()

    out = open(out_file, 'w')

    for path in paths:
        result = transcript_IBM(path)
        out.write(result)
    out.close()

#
# a = transcript_IBM('D:/PROJECT_SPRING/french_db/Spring_Colleague1/Spring_Colleague1_0.wav')
# print(str(a))
