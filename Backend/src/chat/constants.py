import re

CHAT_AVATAR_GROUP_DEFAULT = 'b1762b2c-3afb-4fd6-9590-53f6abdd2b0e.png'
NO_OF_MSG_TO_LOAD = 10
ALLOWED_MSG_CMDS = ['invite']

# Dictionary where:
#   - Keys are command names ("invite", "something_else").
#   - Values are tuples: (List of regex patterns, List of argument names).
ALLOWED_MSG_CMDS_PATTERNS = {
    "invite": ([re.compile(r"^\*\*invite/powerups=(\w+)/map=(\w+)\*\*$")], ["powerups", "map", "localGame"]),
    "something_else": ([re.compile(r"^\*\*something_else/(\w+)\*\*$")], ["a"])
}