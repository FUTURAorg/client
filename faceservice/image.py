import cv2
import base64
import time


import grpc
from futuracommon.protos import imageservice_pb2
from futuracommon.protos import imageservice_pb2_grpc

import logging

import numpy as np
logger = logging.getLogger('FUTURAClient')

def capture_frames(addr):
    # Start capturing video from the webcam
    logger.info("Starting video device...")
    cap = cv2.VideoCapture(0)
    logger.info("Started video device")
    
    try:
        with grpc.insecure_channel(addr) as channel:
            stub = imageservice_pb2_grpc.ImageStreamServiceStub(channel)
            def actual():
                сounter = 0
                while True:
                    # Capture frame-by-frame
                    ret, frame = cap.read()
                    if not ret:
                        print("Failed to grab frame")
                        break

                    retval, buffer = cv2.imencode('.webp', frame)
                    if not retval:
                        print("Failed to encode frame")
                        continue

                    logger.info(f"Got base64 image {сounter}")
                    
                    сounter += 1
                    
                    yield imageservice_pb2.ImageData(client_id="1", image_base64=buffer.tobytes())

                    # Wait for 1 second
                    time.sleep(1)
            res = stub.SendImages(actual())
            logger.info("Closed grpc stream")
    finally:
        # When everything done, release the capture
        cap.release()
        

if __name__ == "__main__":
    capture_frames()