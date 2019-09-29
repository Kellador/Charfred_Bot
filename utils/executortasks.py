import asyncio
import threading
from functools import wraps


class Task():
    def __init__(self, task, loop=asyncio.get_event_loop(),
                 executor=None, event=threading.Event(),
                 count=None, seconds=None, minutes=None, hours=None):
        self.task = task
        self.loop = loop
        self.executor = executor
        self.event = event
        self.count = None
        if not seconds:
            if minutes:
                self.seconds = minutes * 60
            elif hours:
                self.seconds = hours * 3600
        else:
            self.seconds = seconds

    def __call__(self):
        future = self.loop.run_in_executor(self.executor, self.task, self.event)
