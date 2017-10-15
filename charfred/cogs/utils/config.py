import asyncio
import os
import json
import logging as log
from collections.abc import MutableMapping


class Config(MutableMapping):
    """Config MutableMapping for dynamic configuration options;
    Parses data to and from json files.
    """
    def __init__(self, cfgfile, **opts):
        self.cfgfile = cfgfile
        self.loop = opts.pop('loop', asyncio.get_event_loop())
        self.lock = asyncio.Lock()
        if opts.pop('load', False):
            self._load()

    def _load(self):
        try:
            with open(self.cfgfile, 'r') as cf:
                self.cfgs = json.load(cf)
        except FileNotFoundError as e:
            log.warning(f'{self.cfgfile} does not exist, loading as empty dict.')
            self.cfgs = {}
        except IOError as e:
            log.critical(f'Could not load {self.cfgfile}!')

    def _save(self):
        with open(f'{self.cfgfile}.tmp', 'w') as tmp:
            json.dump(self.cfgs.copy(), tmp)
        os.replace(f'{self.cfgfile}.tmp', self.cfgfile)

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
