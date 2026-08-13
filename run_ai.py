from utils.logger import Logger
from processors.ai_processor import AIProcessor

logger = Logger()

processor = AIProcessor(logger)
processor.run()