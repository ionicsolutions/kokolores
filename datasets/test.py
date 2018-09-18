from creator import Creator

c = Creator("dewiki")
dataset = c.create(start=20160101000000, stop=20161231235959,
                   batch_size=50, fname="test2016.json.bz2")
