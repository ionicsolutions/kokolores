import json
from sseclient import SSEClient as EventSource
from queue import Queue, Empty
from threading import Thread

STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'
WIKIS = ["dewiki"]


def listen(work_queue):
    for event in EventSource(STREAM_URL):
        if event.event == 'message':
            try:
                change = json.loads(event.data)

                if change['wiki'] not in WIKIS:
                    continue

                if change['namespace'] != 0:
                    continue

                if change['type'] not in ('new', 'edit'):
                    continue

                rev_id = change['revision']['new']
                print(rev_id, change['title'], change['user'])
                work_queue.put((change['revision']['new'],
                                change['revision']['old']))
            except ValueError:
                pass


def handle(work_queue):
    i = 0
    while True:
        try:
            rev_id, parent_id = work_queue.get_nowait()
        except Empty:
            pass
        else:
            print(rev_id, parent_id)
            i += 1
        if i > 10:
            break

if __name__ == "__main__":
    work_queue = Queue()
    worker = Thread(target=handle, kwargs={"work_queue": work_queue})
    worker.start()
    listen(work_queue)