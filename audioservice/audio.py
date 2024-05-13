import numpy as np
import pyaudio as pa

import librosa

import grpc
import queue
import pyaudio
from futuracommon.protos import audioservice_pb2
from futuracommon.protos import audioservice_pb2_grpc


import logging

logger = logging.getLogger('FUTURAClient')

audio_queue = queue.Queue()

def callback(in_data, frame_count, time_info, status):
        logger.debug(f"{frame_count}, {time_info}, {status}")
        
        audio_queue.put(in_data)
        
        return (None, pyaudio.paContinue)


def vad(ndarray, threshold=5000):
    """ Simple Voice Activity Detection: returns True if voice is detected """
    energy = np.sum(ndarray.astype(float)**2) / len(ndarray)
    # print(energy)
    return energy > 10**8

def audio_processing():

    p = pa.PyAudio()

    CHANNELS = 1
    FRAME_LEN = 0.5
    SAMPLE_RATE = 16000
    CHUNK_SIZE = int(FRAME_LEN*SAMPLE_RATE)

    dev_idx = 1
    
    logger.info(f"Starting PyAudio stream with {CHANNELS} channels, {SAMPLE_RATE} sample rate and {FRAME_LEN}s frame lenght")

    stream = p.open(format=pa.paFloat32,
                    channels=CHANNELS,
                    rate=SAMPLE_RATE,
                    input=True,
                    input_device_index=dev_idx,
                    stream_callback=callback,
                    frames_per_buffer=CHUNK_SIZE)
    stream.start_stream()
    
    logger.info('Listening...')

    try:
        while stream.is_active():
            data = audio_queue.get()
            if data and vad(np.frombuffer(data, dtype=np.int16)):
                yield audioservice_pb2.AudioChunk(audio_data=data, client_id="1")
            
    finally:        
        stream.stop_stream()
        stream.close()
        p.terminate()

        logger.info("PyAudio stopped")

def run_listening(addr):
    with grpc.insecure_channel(addr) as channel:
        stub = audioservice_pb2_grpc.AudioStreamerStub(channel)
        response = stub.StreamAudio(audio_processing())
        print("Streamer client received: " + response.message)