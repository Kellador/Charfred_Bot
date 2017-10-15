import time


class mojException(Exception):
    def __init__(self, message):
        self.message = message


async def getUUID(name, session):
    async with session.get('https://api.mojang.com/users/profiles/minecraft/' +
                           name + '?at=' + str(int(time.time()))) as r:
        if r.status != 204:
            return await r.json()['id']
        else:
            return None


async def getUserData(name, session):
    async with session.get('https://api.mojang.com/users/profiles/minecraft/' +
                           name + '?at=' + str(int(time.time()))) as r:
        if r.status != 204:
            d = r.json()
        else:
            raise mojException("Either the username does not exist or Mojang has troubles!")
    currName = d['name']
    uuid = d['id']
    if 'demo' in d:
        demo = True
    else:
        demo = None
    if 'legacy' in d:
        legacy = True
    else:
        legacy = None
    async with session.get('https://api.mojang.com/user/profiles/' + uuid +
                           '/names') as r:
        d = r.json()
    if len(d) > 1:
        nameHistory = []
        for names in d[1:]:
            nameHistory.append(names['name'])
    else:
        nameHistory = None
    return currName, uuid, demo, legacy, nameHistory


class MCUser:
    def __init__(self, name):
        self.name = name

    async def _init(self, session):
        self.currName, self.uuid, self.demo,
        self.legacy, self.nameHistory = await getUserData(self.name, session)
