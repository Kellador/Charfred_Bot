#!/usr/bin/env python

from .. import configs as cfg


async def getPasteKey(session):
    async with session as cs:
        async with cs.post(
            'https://pastebin.com/api/api_login.php',
            params={'api_dev_key': cfg.pastebinToken,
                    'api_user_name': cfg.pastebinUser,
                    'api_user_password': cfg.pastebinPass}) as resp:
            return await resp.text()
