import asyncio
import os
# This example uses aiofile for asynchronous file reads.
# It's not a dependency of the project but can be installed
# with `pip install aiofile`.
from asyncio.tasks import Task

import aiofile
from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent, TranscriptResultStream

"""
Here's an example of a custom event handler you can extend to
process the returned transcription results as needed. This
handler will simply print the text out to your interpreter.
"""


class MyEventHandler(TranscriptResultStreamHandler):
    def __init__(self, transcript_result_stream: TranscriptResultStream):
        super().__init__(transcript_result_stream)
        self.transcript = []

    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        # This handler can be implemented to handle transcriptions as needed.
        # Here's an example to get started.
        self.transcript = []
        results = transcript_event.transcript.results
        for result in results:
            if not result.is_partial:
                self.transcript.append(result.alternatives[0].transcript)


async def basic_transcribe(audio_file, result):
    # Setup up our client with our chosen AWS region
    client = TranscribeStreamingClient(region="eu-west-2")

    # Start transcription to generate our async stream
    stream = await client.start_stream_transcription(
        language_code="fr-FR",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )

    async def write_chunks():
        # An example file can be found at tests/integration/assets/test.wav
        # NOTE: For pre-recorded files longer than 5 minutes, the sent audio
        # chunks should be rate limited to match the realtime bitrate of the
        # audio stream to avoid signing issues.
        async with aiofile.AIOFile(audio_file, 'rb') as afp:
            reader = aiofile.Reader(afp, chunk_size=1024 * 16)
            async for chunk in reader:
                await stream.input_stream.send_audio_event(audio_chunk=chunk)
        await stream.input_stream.end_stream()

    # Instantiate our handler and start processing events
    handler = MyEventHandler(stream.output_stream)
    await asyncio.gather(write_chunks(), handler.handle_events())
    if len(handler.transcript) > 0:
        result.append(handler.transcript[0])
    else:
        result.append("")


def transcribe_from_file(audio_file):
    result = []
    print(audio_file)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(basic_transcribe(audio_file, result))
    # loop.close()
    # asyncio.run(basic_transcribe(audio_file, result))
    return result[0]


def transcribe_from_wavscp(wav_scp_path, out_file):
    wav_scp = open(wav_scp_path, 'r')
    lines = wav_scp.readlines()
    result = []
    paths = []
    for line in lines:
        _, path = line.split(' ')
        paths.append(path[:-1])

    wav_scp.close()

    out = open(out_file, 'w', encoding='utf-8')

    for path in paths:
        result = transcribe_from_file(path)
        out.write(result + "\n")
    out.close()


