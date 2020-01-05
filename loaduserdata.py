import json
from cogs.logger import logger
from cogs.user import PlayerWrapper

"""
    This has led to alot of confusion when I initially wrote it, so i'm writing out exactly how it works to make sure
    dumb ol' me can always remember, or at least piece together in a reasonable amount of time, whats happening.  
    Future me; if the documentation isn't enough, im sorry and please continue to ELI5.
"""

__playerData__ = {}  # Global variable that will eventually hold the entire Player object structure.  A quick diagram
# of what
# it should look like:
"""
                            __playerData__ (Dictionary Object (UID, Player Object) )
                                |
                                v
                            Player Objects (Stores the user ID and list of PC's each user has) which contains a PCDict 
                            (Dictionary of PC's the users have)
                                |
                                v
                            PC Objects (Stores PC variables and member functions to manipulate them)

"""


def loaddata(bot):
    _playerDict = {}  # A JSON-writeable nested dict structure to be constructed while data is loading
    _jsonDict = json.load(open('data/userdata.json', 'r'))  # Loads a Dict(Player Object) of Dicts(PC Objects)

    for usr in bot.get_all_members():  # Gets a list of all members in the Discord to iterate through
        if usr.id in _jsonDict:  # If the user's ID already has a Player Dict in _jsonDict:
            _playerDict[usr.id] = _jsonDict[
                usr.id]  # Store that Key, Value pair in the _playerDict dict we are constructing
            __playerData__[usr.id] = PlayerWrapper.Player(bot=bot, load_from_dict=_jsonDict[
                usr.id])  # Initialize Player Object(Which contains an empty PCdict)
            for key, pc in _jsonDict[usr.id]["PCdict"].items():  # For each PC the Player has in their PCdict
                _playerDict[usr.id]["PCdict"][key] = pc  # Store that Key, Value pair in the _playerDict
                __playerData__[usr.id].addPC(key, PlayerWrapper.PC(
                    load_from_dict=_jsonDict[usr.id]["PCdict"][key]))  # Initialize PC Object

        else:
            logger.info(f'generating {usr}')
            _playerDict[usr.id] = PlayerWrapper.Player(bot=bot, member=usr).__dict__
            __playerData__[usr.id] = PlayerWrapper.Player(bot=bot, member=usr)
        json.dump(_playerDict, open('data/userdata.json', 'w'), indent=4)


def savedata():
    _playerDict = {}  # A JSON-writeable nested dict structure to be constructed while data is loading
    for usr in __playerData__:
        _playerDict[usr] = json.loads(__playerData__[usr].toJSON())
    json.dump(_playerDict, open('data/userdata.json', 'w'), indent=4)
