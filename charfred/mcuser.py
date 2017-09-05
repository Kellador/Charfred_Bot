import requests
import time


class mojException(Exception):
    def __init__(self, message):
        self.message = message


def getUUID(name):
    r = requests.get('https://api.mojang.com/users/profiles/minecraft/' +
                     name + '?at=' + str(int(time.time())))
    if r.ok and r.status_code != 204:
        return r.json()['id']
    else:
        return None


def getUserData(name):
    r = requests.get('https://api.mojang.com/users/profiles/minecraft/' +
                     name + '?at=' + str(int(time.time())))
    if r.ok and r.status_code != 204:
        r = r.json()
    else:
        raise mojException("Either the username does not exist or Mojang has troubles!")
    currName = r['name']
    uuid = r['id']
    if 'demo' in r:
        demo = True
    else:
        demo = None
    if 'legacy' in r:
        legacy = True
    else:
        legacy = None
    r = requests.get('https://api.mojang.com/user/profiles/' + uuid + '/names').json()
    if len(r) > 1:
        nameHistory = []
        for names in r[1:]:
            nameHistory.append(names['name'])
    else:
        nameHistory = None
    return currName, uuid, demo, legacy, nameHistory


class MCUser:
    def __init__(self, name, uuid=None, demo=None, legacy=None, nameHistory=None):
        self.name, self.uuid, self.demo, self.legacy, self.nameHistory = getUserData(name)
