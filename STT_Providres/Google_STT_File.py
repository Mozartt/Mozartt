"""Streams transcription of the given audio file."""
import io
import time
# beta library. supports more configurations that are still being tested.
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
import time


class STTFromStreamGoogle:
    def __init__(self):
        self.provider = 'google'

    # this is a generator. if you are not familiar with this tool, i recommend reading this:
    # https://www.programiz.com/python-programming/generator is is basically an iterator. this generator yields a
    # frame of audio on each call. i also added a sleep command to make kind of real time.
    def stream_generator(self, content, chunk=1024 * 16):
        size = len(content)
        num_chunks = int(size // chunk)
        for i in range(num_chunks):
            #time.sleep(1)
            yield content[i * chunk:(i + 1) * chunk]

    def SendAudio(self, file_path, lang, RATE):

        # get the credentials from the creds file. it is available to download in the google cloud site.
        credentials = service_account.Credentials.from_service_account_file('D:\PROJECT_SPRING\SPRING\CredentialsKeys\Google_key.json')
        # Instantiates a client
        client = speech.SpeechClient(credentials=credentials)

        # file path. note that not all wav formats are supported.
        stream_file = file_path

        # read the file as bytes.
        with io.open(stream_file, "rb") as audio_file:
            content = audio_file.read()

        # here i instantiate the generator.
        stream = self.stream_generator(content)

        # this is also an generator!
        requests = (
            speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
        )

        # select the configuration.
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=lang,
            enable_word_time_offsets=True,
        )

        # make it a streaming config.
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=False)

        # streaming_recognize returns a generator.
        responses = client.streaming_recognize(
            config=streaming_config,
            requests=requests,
        )
        start = time.time()
        return [[response, time.time() - start] for response in responses]

        # iterate through the returned generator.
        # for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.

        # for result in response.results:
        # print("Finished: {}".format(result.is_final))
        # print("Stability: {}".format(result.stability))
        # alternatives = result.alternatives
        # # The alternatives are ordered from most likely to least.
        # for alternative in alternatives:
        #     print("Confidence: {}".format(alternative.confidence))
        #     print(u"Transcript: {}".format(alternative.transcript))
