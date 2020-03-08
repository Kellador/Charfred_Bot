from .config import Config
from .invertableconfig import InvertableConfig
from .permissions import permission_node, node_check
from .mixed import cached_property, splitup
from .context import CharfredContext
from .flipbooks import Flipbook, EmbedFlipbook
from .collections import SimpleTTLDict, SizedDict

# Colors from http://colourlovers.com;
# names correspond to the color names on the site.
invisible_ufo = ('00A0B0', 41136)
caribic_brown = ('6A4A3C', 6965820)
caribic_red = ('CC333F', 13382463)
caribic_sun = ('EB6841', 15427649)
caribic_daylight = ('EDC951', 15583569)
flat_bone = ('EDEBE6', 15592422)
heart_of_gold = ('FBB829', 16496681)
hot_pink = ('FF0066', 16711782)
mighty_slate = ('556270', 5595760)


palette = {
    'cyan': invisible_ufo,
    'brown': caribic_brown,
    'red': caribic_red,
    'orange': caribic_sun,
    'yellow': caribic_daylight,
    'white': flat_bone,
    'gold': heart_of_gold,
    'pink': hot_pink,
    'slate': mighty_slate
}
