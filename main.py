from multiprocessing import Process

from audioservice.audio import run_listening
from faceservice.image import capture_frames

import logging

from syntservice.main import consume

logging.basicConfig(level=logging.INFO,  # Set minimum log level to DEBUG
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = logging.getLogger('FUTURAClient')

if __name__ == '__main__':
    
    logger.info("initialization audio process")
    audio = Process(target=run_listening, kwargs={"addr": "127.0.0.1:50051"})
    audio.start()
    
    logger.info("initialization images process")
    images = Process(target=capture_frames, kwargs={"addr": "127.0.0.1:50052"})
    images.start()
    
    logger.info("initialization sound player")
    sound = Process(target=consume, kwargs={"addr": "127.0.0.1:50054"})
    sound.start()