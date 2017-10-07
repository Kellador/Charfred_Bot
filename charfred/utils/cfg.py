import asyncio
import os
import json
import logging as log
from collections.abc import MutableMapping


class Config(MutableMapping):
    """Config MutableMapping for dynamic configuration options;
    Parses data to and from json files.
    """
    def __init__(self, name, **opts):
        self.name = name
        self.loop = opts.pop('loop', asyncio.get_event_loop())
        self.lock = asyncio.Lock()
        self._load()

    def _load(self):
        try:
            with open(self.name, 'r') as cf:
                self.cfgs = json.load(cf)
        except IOError as e:
            log.critical(f'Could not load {self.name}!')

    def _save(self):
        with open(f'{self.name}.tmp', 'w') as tmp:
            json.dump(self.cfgs.copy(), tmp)
        os.replace(f'{self.name}.tmp', self.name)

    async def save(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._save())

    async def load(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._load())

    def __getitem__(self, key):
        return self.cfgs[key]

    def __iter__(self):
        return iter(self.cfgs)

    def __len__(self):
        return len(self.cfgs)

    def __setitem__(self, key, value):
        self.cfgs[key] = value

    def __delitem__(self, key):
        del self.cfgs[key]
