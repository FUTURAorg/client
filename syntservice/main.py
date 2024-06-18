import multiprocessing
from time import sleep
import grpc
import numpy as np
from futuracommon.protos import tts_pb2
from futuracommon.protos import tts_pb2_grpc

import sounddevice

def consume(addr, session_id = "1"):
    channel = grpc.insecure_channel(addr,
                                    options=[
        ('grpc.max_receive_message_length', 30*24000*8),
    ],)
    stub = tts_pb2_grpc.TextToSpeechStub(channel)
    
    print("Start consuming...")
    for audio_chunk in stub.StreamAudio(tts_pb2.StreamRequest(session_id=session_id)):
        print("Received Audio Chunk: ", len(audio_chunk.data))
        sound = np.frombuffer(audio_chunk.data)
        sounddevice.play(sound, 24000)
        sounddevice.wait()
        
        
        
def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = tts_pb2_grpc.TextToSpeechStub(channel)    
    while True:
        text = input()
        response = stub.ProcessText(tts_pb2.TextRequest(text=text, session_id="1"))
        session_id = response.session_id
        print(f"Session id: {session_id}")

if __name__ == '__main__':
    consumer = multiprocessing.Process(target=consume)
    consumer.start()