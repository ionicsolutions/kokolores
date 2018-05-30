import logging
from creator import Creator

c = Creator("dewiki")
dataset = c.create(10000, batch_size=100, fname="dewiki_10000.json.bz2")
