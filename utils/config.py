import asyncio
import logging
import json
import toml
from pathlib import Path
from collections.abc import MutableMapping

log = logging.getLogger('charfred')


class Config(MutableMapping):
    """Config MutableMapping for dynamic configuration options;
    Parses data to and from json or toml files.
    """

    def __init__(self, cfgfile, **opts):
        self.cfgfile = Path(cfgfile)
        self.loop = opts.pop('loop', None)
        self.lock = asyncio.Lock()
        self.default = opts.pop('default', None)
        self.toml = True if self.cfgfile.suffix == '.toml' else False
        if self.toml:
            self.loadfunc = toml.load
            self.dumpfunc = toml.dump
        else:
            self.loadfunc = json.load
            self.dumpfunc = json.dump
        if opts.pop('load', False):
            self._load()

    def _convert(self):
        if self.toml:
            convertee = self.cfgfile.with_suffix('.json')
            if convertee.exists():
                self.loadfunc = json.load

    def _load(self):
        convertee = self.cfgfile.with_suffix('.json') if self.toml else self.cfgfile.with_suffix('.toml')
        if convertee.exists():
            log.info(f'{self.cfgfile} already exists as {convertee}; Loading and converting...')
            loadfile = convertee
            loadfunc = json.load if self.toml else toml.load
        else:
            loadfile = self.cfgfile
            loadfunc = self.loadfunc
        try:
            with open(loadfile, 'r') as cf:
                self.store = loadfunc(cf)
            log.info(f'{loadfile} loaded.')
        except FileNotFoundError:
            log.warning(f'{loadfile} does not exist.')
            if self.default:
                if isinstance(self.default, dict):
                    self.store = self.default
                    log.info(f'Initiated {loadfile} from given dictionary!')
                else:
                    self._loadDefault()
                    log.info(f'Initiated {loadfile} from {self.default}!')
            else:
                self.store = {}
                log.info('Loaded as empty dict!')
        except IOError:
            log.critical(f'Could not load {loadfile}!')
            self.store = {}
            log.info('Loaded as empty dict!')
        if convertee.exists():
            self._save()
            convertee.unlink()
            log.info(f'Deleted {convertee}.')

    def _loadDefault(self):
        try:
            with open(self.default, 'r') as cf:
                self.store = self.loadfunc(cf)
            self._save()
        except IOError:
            log.warning(f'{self.default} does not exist.')
            self.store = {}
            log.info('Loaded as empty dict!')

    def _save(self, savee=None):
        if savee is None:
            savee = self.store
        self.cfgfile.parent.mkdir(parents=True, exist_ok=True)
        tmpfile = self.cfgfile.with_suffix('.tmp')
        with open(tmpfile, 'w') as tmp:
            self.dumpfunc(savee.copy(), tmp)
        tmpfile.replace(self.cfgfile)

    async def save(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._save)

    async def load(self):
        with await self.lock:
            await self.loop.run_in_executor(None, self._load)

    def __getitem__(self, key):
        return self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]
