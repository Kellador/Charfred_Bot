import logging
from utils import Config

log = logging.getLogger('charfred')


class InvertableConfig(Config):
    """Subclass of Config, which generates and updated
    an inverted read only version of its store.
    """

    def __init__(self, cfgfile, **opts):
        super().__init__(cfgfile, **opts)
        self._inverted = {}

    @property
    def inverted(self):
        if self._inverted:
            return self._inverted
        else:
            try:
                self._invert()
            except AttributeError:
                pass  # Too early, Config hasn't loaded yet.
            finally:
                return self._inverted

    def _invert(self):
        self._inverted = {}
        for k, v in self.cfgs.items():
            self._inverted.setdefault(v, []).append(k)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._invert()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._invert()
