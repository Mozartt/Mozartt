from __future__ import division

import re
import sys

# beta library. supports more configurations that are still being tested.
from google.cloud import speech_v1p1beta1 as speech

from google.oauth2 import service_account

import pyaudio
from six.moves import queue

# read the Google_STT_File.py before. it is much more simple, but has the same idea.

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

# get the credentials from the creds file. it is available to download in the google cloud site.
credentials = service_account.Credentials.from_service_account_file('C:/Users/Amit/Documents/ASR_keys/Google_key.json')


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]

        print(result)



# See http://g.co/cloud/speech/docs/languages
# for a list of supported languages.
language_code = "en-US"  # a BCP-47 language tag

# get the credentials from the creds file. it is available to download in the google cloud site.
client = speech.SpeechClient(credentials=credentials)

# select the configuration.
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code=language_code,
    enable_word_time_offsets=True,
    enable_word_confidence=True,  # this is an example of a configuration only available at the beta library.
)

# make it a streaming config.
streaming_config = speech.StreamingRecognitionConfig(
    config=config, interim_results=True,

)

with MicrophoneStream(RATE, CHUNK) as stream:
    # instantiate the data generator.
    audio_generator = stream.generator()

    # iterate through it.
    requests = (
        speech.StreamingRecognizeRequest(audio_content=content)
        for content in audio_generator
    )

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(streaming_config, requests)

    # Now, put the responses received.
    listen_print_loop(responses)

