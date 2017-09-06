#!/usr/bin/env python

import discord
import configs as cfg
import keywords
import re
import random
import requests
import pexpect as pexp
import os
from gzip import GzipFile
from mcuser import getUUID, MCUser, mojException
from nbt import NBTObj, TAG_List, TAG_Compound
from ttldict import TTLOrderedDict

serverRX = re.compile(('|'.join(map(re.escape, list(cfg.servers.keys())))))
rawPattern = '(({})\s*.*?((?=\s*and|,)|(?=\s*[^\w\+\-\d]*$)|(?=\s*({}))|(?=\s*,?\s*({})$)))'.format(
    '|'.join(list(cfg.commands.keys())),
    '|'.join(list(cfg.commands.keys())),
    '|'.join(map(re.escape, keywords.keyphrases)))
cmdPattern = re.compile(rawPattern)
sshReplyPattern = re.compile('\[Timestamp\].*')
description = ('Charfred is a gentleman through and through,'
               ' he will do almost anything you ask of him.'
               ' He can be quite rude however.')
charfred = discord.Client(max_messages=1000)
pastebin_user_key = requests.post('https://pastebin.com/api/api_login.php',
                                  data={'api_dev_key': cfg.pastebinToken,
                                        'api_user_name': cfg.pastebinUser,
                                        'api_user_password': cfg.pastebinPass}).text
print('Pastebin user key is: ' + pastebin_user_key)
playerCache = TTLOrderedDict(default_ttl=60)


def roleCall(user, requiredRole):
    for role in user.roles:
        if role.name in cfg.roles:
            if cfg.roles.index(role.name) >= cfg.roles.index(requiredRole):
                return True


async def cmdResolution(message, c):
    if message.server.id in cfg.commandCh.keys():
        searchCh = cfg.commandCh[message.server.id]
        for ch in message.server.channels:
            if ch.id == searchCh:
                targetCh = ch
                break
    else:
        print('ERROR: No valid commandCh found!')
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.errormsgs) +
                                     '\n' + c))
        return
    if re.search('[^\w,+\- ]', c):
        print('Buggery detected! ' + c + ' by ' + message.author.name)
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.errormsgs) +
                                     '\n' + c))
        return
    if (roleCall(message.author, cfg.commands[c.split()[0]]['MinRank'])):
        print('Command accepted! ' + c)
        await charfred.send_message(message.channel,
                                    random.choice(keywords.acks))
        await charfred.send_typing(message.channel)
        response = await globals()[cfg.commands[c.split()[0]]['Type']](c)
        # if cfg.commands[c.split()[0]]['Type'] == 'stalkCmd':
        if type(response) is discord.Embed:
            await charfred.send_message(targetCh,
                                        embed=response)
        else:
            await charfred.send_message(targetCh,
                                        (random.choice(keywords.replies) +
                                         response))
        if message.channel.id != targetCh.id:
            await charfred.send_message(message.channel,
                                        (random.choice(keywords.deposits) +
                                         ' ' + targetCh.mention))
    else:
        print('No permission! ' + c)
        await charfred.send_message(message.channel,
                                    (random.choice(keywords.errormsgs) +
                                     '\n' + c))


async def serverCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    response = ['```']
    for server in cSplit[1:]:
        if (server in cfg.servers) and (cmd not in cfg.servers[server]):
            sshcmd = cfg.commands[cmd]['Pattern'].format(
                ssh=cfg.sshName,
                script=cfg.commands[cmd]['Script'],
                cmd=cmd,
                args=server)
            sshRpl = sshReplyPattern.search(
                pexp.run(sshcmd, events={'(?i)(passphrase|password)':
                                         cfg.sshPass}).decode()).group(0)
            response.append(sshRpl)
            # response.append(sshcmd)
        else:
            print('Invalid target! {}'.format(server))
            response.append(('Invalid target! {}'.format(server)))
    response.append('```')
    return ('\n'.join(response))


async def playerCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    response = ['```']
    if len(cSplit) > 2:
        argument = " " + cSplit[2]
    else:
        argument = ""
    sshcmd = cfg.commands[cmd]['Pattern'].format(
        ssh=cfg.sshName,
        script=cfg.commands[cmd]['Script'],
        cmd=cmd,
        args=cSplit[1] + argument)
    sshRpl = sshReplyPattern.search(
        pexp.run(sshcmd, events={'(?i)(passphrase|password)':
                                 cfg.sshPass}).decode()).group(0)
    response.append(sshRpl)
    # response = sshcmd
    response.append('```')
    return ('\n'.join(response))


async def specialCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    response = ['```']
    sshcmd = cfg.commands[cmd]['Pattern'].format(
        ssh=cfg.sshName,
        script=cfg.commands[cmd]['Script'],
        cmd=cmd,
        args=' '.join(cSplit[1:]))
    sshRpl = sshReplyPattern.search(
        pexp.run(sshcmd, events={'(?i)(passphrase|password)':
                                 cfg.sshPass}).decode()).group(0)
    response.append(sshRpl)
    # response = sshcmd
    response.append('```')
    return ('\n'.join(response))


async def reportCmd(c):
    cSplit = c.split()
    cmd = cSplit[0]
    sshcmd = cfg.commands[cmd]['Pattern'].format(
        ssh=cfg.sshName,
        script=cfg.commands[cmd]['Script'],
        cmd=cmd,
        args=' '.join(cSplit[1:]))
    response = sshReplyPattern.search(
        pexp.run(sshcmd, events={'(?i)(passphrase|password)':
                                 cfg.sshPass}).decode()).group(0)
    # response = sshcmd
    data = {'api_dev_key': cfg.pastebinToken,
            'api_option': 'paste',
            'api_paste_code': response,
            'api_user_key': pastebin_user_key,
            'api_paste_private': '2',
            'api_paste_expire_date': '10M'}
    return requests.post('https://pastebin.com/api/api_post.php', data=data).text


async def stalkCmd(c):
    lookupName = c.split()[1]
    playerCache._purge()
    if lookupName in playerCache:
        mcU = playerCache.get(lookupName)
        print('Cached!')
    else:
        try:
            mcU = MCUser(lookupName)
        except mojException:
            print(mojException.message)
            return discord.Embed(title="ERROR",
                                 type="rich",
                                 colour=discord.Colour.dark_red())
    playerCache[lookupName] = mcU
    reportCard = discord.Embed(title="__Subject: " + mcU.name + "__",
                               url='http://mcbouncer.com/u/' + mcU.uuid,
                               type='rich',
                               color=0x0080c0)
    reportCard.set_author(name="Classified Report",
                          url='https://google.com/search?q=minecraft%20' + mcU.name,
                          icon_url='https://crafatar.com/avatars/' + mcU.uuid)
    reportCard.set_thumbnail(url='https://crafatar.com/renders/head/' +
                             mcU.uuid + '?overlay')
    reportCard.add_field(name="Current Name:",
                         value="```\n" + mcU.name + "\n```")
    reportCard.add_field(name="UUID:",
                         value="```\n" + mcU.uuid + "\n```")
    if mcU.demo:
        reportCard.add_field(name="__**DEMO ACCOUNT**__")
    if mcU.legacy:
        reportCard.add_field(name="*Legacy*")
    if mcU.nameHistory is not None:
        pastNames = ', '.join(mcU.nameHistory)
        reportCard.add_field(name="Past names:",
                             value=pastNames)
    reportCard.set_footer(text="Report compiled by Agent Charfred")
    return reportCard


async def editNBT(msg):
    # TODO: (.{8})-?(.{4})-?(.{4})-?(.{4})-?(.{12})
    print('Starting interactive NBT session')
    await charfred.send_message(msg.channel,
                                'Please reply with the name of the server'
                                'and the user that you want to work on.')
    rep = await charfred.wait_for_message(author=msg.author,
                                          channel=msg.channel)
    server = rep.content.split()[0]
    user = rep.content.split()[1]
    if server not in cfg.servers:
        await charfred.send_message(msg.channel, 'Sorry, that server name is invalid!')
        return
    # NOTE: Test code follows, implement fetching from server later.
    filepath = os.path.join(cfg.nbtPath, '2bffdcf2-732f-40e2-b024-826475a47f4e.dat')
    with open(filepath, 'rb') as io:
        io = GzipFile(fileobj=io)
        nbt = NBTObj(io=io)
        io.close()
    tagnames = []
    for tag in nbt.value:
        if type(tag) is TAG_List or type(tag) is TAG_Compound:
            tagnames.append(tag.name + ' : ' + str(len(tag.value)) + ' Entries')
        else:
            tagnames.append(tag.name + ' : ' + str(tag.value))
        # tagnames.append(tag.name)
    tagnames = sorted(tagnames, key=str.lower)
    listTags = '\n'.join(tagnames)
    while True:
        await charfred.send_message(msg.channel,
                                    'Tags:\n```\n' + listTags + '\n```\n' +
                                    'Please reply with the name of the Tag to edit!')
        targetTag = await charfred.wait_for_message(author=msg.author,
                                                    channel=msg.channel)
        for tag in nbt.value:
            if tag.name == targetTag:
                targetTag = tag
                break
        if type(targetTag) is TAG_List:
            await charfred.send_message(msg.channel,
                                        'Tags to edit:\n```\n' +
                                        '\n'.join(targetTag.value) +
                                        '\n```')
            for tag in targetTag.value:
                n = 1
                await charfred.send_message(msg.channel,
                                            'Please enter the new value for Tag' +
                                            str(n))
                n += 1
                newVal = await charfred.wait_for_message(author=msg.author,
                                                         channel=msg.channel)


@charfred.event
async def on_ready():
    print('Logged in as:')
    print(charfred.user.name)
    print(charfred.user.id)
    print('=============')


@charfred.event
async def on_message(message):
    if message.channel.id in cfg.allowedCh:
        msg = message.content
        cmds = cmdPattern.findall(msg)
        if (msg.startswith('Charfred,') and len(cmds) > 0):
            # cmdList = [re.sub('[^\w\+ ]', '', n[0]) for n in cmds]
            cmdList = [n[0] for n in cmds]
            print('Command recieved!')
            print(*cmdList, sep='\n')
            print(message.author.name)
            for c in cmdList:
                await cmdResolution(message, c)
        elif (msg.startswith('Charfred,') and ' nbt' in msg):
            await editNBT(message)
        elif (msg.startswith('Charfred,')):
            await charfred.send_message(message.channel,
                                        random.choice(keywords.nacks))


if cfg.liveMode:
    charfred.run(cfg.liveBotToken)
else:
    charfred.run(cfg.stageBotToken)
