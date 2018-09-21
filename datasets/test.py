import logging

from creator import Creator

logging.basicConfig(level=logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logger = logging.getLogger()
fh = logging.FileHandler("creator.log")
logger.addHandler(fh)
logger.info("Starting...")
c = Creator("dewiki")
dataset = c.create(start=20170101000000, stop=20171231235959,
                   batch_size=50, fname="test2017.json.bz2")

