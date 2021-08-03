import time
import wave
import json
import azure.cognitiveservices.speech as speechsdk
import logging


def transcribe(audio_file_path, credentials):
    # import the credentials from the json file
    results = []

    with open(credentials) as json_file:
        creds = json.load(json_file)
    # create the speech configuration
    speech_config = speechsdk.SpeechConfig(subscription=creds["key"], region=creds["region"],
                                           speech_recognition_language="fr-FR")

    # enable different features if needed
    channel = speechsdk.ServicePropertyChannel.UriQueryParameter

    speech_config.set_service_property(name='wordLevelConfidence', value='true', channel=channel)
    speech_config.set_service_property(name='format', value='detailed', channel=channel)
    speech_config.request_word_level_timestamps()

    # setup the audio stream
    stream = speechsdk.audio.PushAudioInputStream()
    audio_config = speechsdk.audio.AudioConfig(stream=stream)

    # instantiate the speech recognizer with push stream input
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def OnRecogniztionFinish(evt):
        results.append(evt.result.text)
        print(evt.result.text)

    # Connect callbacks to the events fired by the speech recognizer
    # speech_recognizer.recognizing.connect(lambda evt: print())
    speech_recognizer.recognized.connect(OnRecogniztionFinish)
    # speech_recognizer.session_started.connect(lambda evt: print("started"))
    # speech_recognizer.session_stopped.connect(lambda evt: print("stopped"))
    speech_recognizer.canceled.connect(lambda evt: print("canceled"))

    # The number of bytes to push per buffer
    n_bytes = 2048
    wav_fh = wave.open(audio_file_path)
    # print(audio_file_path)
    # start continuous speech recognition
    speech_recognizer.start_continuous_recognition()

    # start pushing data until all data has been read from the file
    try:
        while True:
            frames = wav_fh.readframes(n_bytes // 2)
            # print('read {} bytes'.format(len(frames)))

            # when the file has ended, send empty bytes and exit the loop
            if not frames:
                stream.write(bytes([]))
                break

            # send the bytes
            stream.write(frames)
            # waiting 0.1 seconds before proceeding, to imitate real time. not mandatory.
            # time.sleep(.1)
    finally:
        # wait for all the responses to come back. 5 seconds might be a lot, but it will be surely enough...
        time.sleep(5)

        # stop recognition and clean up
        wav_fh.close()
        stream.close()
        speech_recognizer.stop_continuous_recognition()
        print("manual cancel")
        if len(results) > 0:
            return results[0]
        return ""


def transcribe_from_file(wav_scp_file, out_file, credentials):
    wav_scp = open(wav_scp_file, 'r')
    lines = wav_scp.readlines()

    paths = []
    for line in lines:
        _, path = line.split(' ')
        paths.append(path[:-1])

    wav_scp.close()
    # out = open(out_file, 'w', encoding='utf-8')
    out = open(out_file, 'w')

    for path in paths:
        result = transcribe(path, credentials)
        out.write(result + "\n")
    out.close()
