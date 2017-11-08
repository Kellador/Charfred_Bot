import os
import importlib
import click
from cogs.utils.config import Config

botDir = os.path.dirname(os.path.realpath(__file__))

cfg = Config(f'{botDir}/cogs/configs/botCfg.json')


def _cogs():
    for _cog in os.listdir(f'{botDir}/cogs'):
        if os.path.isfile(os.path.join(f'{botDir}/cogs', _cog)):
            yield _cog[:-3]


def _nodes():
    click.echo('We\'ll set up the permission nodes for all currently '
               'installed cogs (extensions) now. If the cog defines '
               'checks for its functions then these checks will run '
               'against these permissions.\n'
               'For every permission node you will be asked to provide '
               'some information. It may take a while if there are a '
               'lot of permission nodes.\n'
               'So let\'s get started!')
    for _cog in _cogs():
        cog = importlib.import_module(f'cogs.{_cog}')
        nodes = getattr(cog, 'permissionNodes', None)
        if nodes is None:
            continue
        click.echo('Beginning setup for permission nodes defined for '
                   f'{_cog}!')
        for node in nodes:
            if node.startswith('spec:'):
                default = nodes[node][1]
                cfg['nodes'][node] = default
                if type(default) is str:
                    if len(nodes[node]) > 2 and nodes[node][2]:
                        spec = click.prompt(nodes[node][0]).split()
                    else:
                        spec = click.prompt(nodes[node][0])
                elif type(default) is bool:
                    spec = click.confirm(nodes[node][0])
                else:
                    if len(nodes[node]) > 2 and nodes[node][2]:
                        spec = click.prompt(nodes[node][0], type=type(default))
                    else:
                        spec = click.prompt(nodes[node][0], type=type(default))
                cfg['nodes'][node] = [spec, nodes[node][0]]
                continue
            cfg['nodes'][node] = {}
            cfg['nodes'][node]['ranks'] = []
            ranks = click.prompt('Please enter all Discord roles which will be '
                                 f'allowed to run \"{node}\", seperated by spaces only!\n').split()
            cfg['nodes'][node]['ranks'] = ranks
            cfg['nodes'][node]['channels'] = []
            if click.confirm('Would you like to define specific channels where '
                             f'{node} will be allowed?\n If you don\'t then '
                             'it will only work in the default command channel!\n'):
                channels = click.prompt('Please enter all channel\' IDs where '
                                        f'\"{node}\" is allowed to be run, seperated by spaces only!\n').split()
                channels = list(map(int, channels))
                cfg['nodes'][node]['channels'] = channels
        else:
            click.echo(f'Done with all permission nodes for {_cog}!')
    else:
        click.echo('Excellent, we\'re all done with the permission nodes now!')


@click.group(invoke_without_command=True)
@click.pass_context
def wizard(ctx):
    if ctx.invoked_subcommand is None:
        cfg._load()
        click.echo('Beginning Charfred setup! yay!\n'
                   'We\'ll be walking through a bunch of configuration options, '
                   'but you don\'t have to work through them all now,'
                   'there will be a breakpoint after the absolute requirements.\n'
                   'If you decide to stop at the breakpoint, you can resume later '
                   'by running \"charwizard nodes\", or you can start the setup over again!\n')
        click.confirm('If you have already ran the wizard before, this will '
                      'reset any configuration options you\'ve already saved!\n'
                      'Are you sure you want to continue?\n', abort=True)
        token = click.prompt('Alright! Please enter your bot token\n')
        cfg['botToken'] = token
        click.echo('We\'ll now setup the prefixes that Charfred will accept '
                   'one by one, you\'ll be asked if you want to add more after '
                   'every one.\n' 'Anything you enter (including whitespace) '
                   'will become a prefix.\n')
        cfg['prefixes'] = []
        prefix = click.prompt('Please enter the first prefix!\n')
        cfg['prefixes'].append(prefix)
        while click.confirm('Wanna add one more?\n'):
            prefix = click.prompt('Please enter another prefix!\n')
            cfg['prefixes'].append(prefix)
        click.echo('Perfect! Now comes the channel ID for the default command '
                   'channel. This will be used in our permission system.\n'
                   'When you run a command the channel where the command is '
                   'issued will be first checked against this ID. '
                   'So all commands will be allowed to run in this channel!')
        defaultCmdCh = click.prompt('Please enter the numeric channel ID now!\n',
                                    type=int)
        cfg['defaultCmdCh'] = defaultCmdCh
        cfg['nodes'] = {}
        cfg._save()
        click.confirm('Great! We\'ve reached the breakpoint! The absolute basics '
                      'have been set up. This next part is gonna a lot longer!\n'
                      'You wanna continue now?\n', abort=True)
        _nodes()
        cfg._save()
        click.echo('All done, yay! You\'re ready to start using Charfred now! '
                   'If you\'ve setup everything correctly that is ;)\n'
                   'If you have any problems you can just run this wizard again!')


@wizard.group(invoke_without_command=True)
@click.pass_context
def nodes(ctx):
    cfg._load()
    click.echo('Loaded existing configs for Charfred.')
    if ctx.invoked_subcommand is None:
        _nodes()
        cfg._save()
        click.echo('Configs for Charfred saved!')


@nodes.command()
def edit():
    while True:
        for node in cfg['nodes']:
            click.echo(node)
        node = click.prompt('Which command\'s permissions would you like to edit?\n'
                            'This will wipe all current permissions for the selected '
                            'command! You\'ll be shown the current permissions and '
                            'then asked to enter new permissions.\n')
        if node not in cfg['nodes']:
            click.echo(f'{node} is not a registered command!')
            return
        if node.startswith('spec:'):
            if type(cfg['nodes'][node][0]) is str:
                spec = click.prompt(cfg['nodes'][node][-1])
            elif type(cfg['nodes'][node][0]) is bool:
                spec = click.confirm(cfg['nodes'][node][-1])
            elif type(cfg['nodes'][node][0]) is list:
                if type(cfg['nodes'][node][0][0]) is str:
                    spec = click.prompt(cfg['nodes'][node][-1]).split()
                else:
                    spec = click.prompt(cfg['nodes'][node][-1],
                                        type=type(cfg['nodes'][node][0])).split()
            cfg['nodes'][node] = [spec, cfg['nodes'][node][-1]]
        else:
            click.echo('Old entries for allowed ranks:\n' +
                       ' '.join(cfg['nodes'][node]['ranks']))
            ranks = click.prompt('Please enter all Discord roles which will be '
                                 f'allowed to run \"{node}\", seperated by spaces only!\n').split()
            cfg['nodes'][node]['ranks'] = ranks
            if click.confirm('Would you like to define specific channels where '
                             f'{node} will be allowed?\n If you don\'t then '
                             f'{node} will only work in the default command channel!\n'):
                click.echo('Old entries for allowed channels:\n' +
                           ' '.join(cfg['nodes'][node]['channels']))
                cfg['nodes'][node]['channels'] = []
                channels = click.prompt('Please enter all Discord channels\' IDs where '
                                        f'\"{node}\" is allowed to be run, seperated by '
                                        'spaces only!\n').split()
                channels = list(map(int, channels))
                cfg['nodes'][node]['channels'] = channels
            click.echo(f'Done editing permissions for {node}!')
        if not click.confirm('Would you like to edit more?\n'):
            break
    cfg._save()


@wizard.command()
def token():
    cfg._load()
    click.echo('Current Token: ' + cfg['botToken'])
    if click.confirm('Would you like to change it?\n'):
        token = click.prompt('Please enter the new Token!\n')
        cfg['botToken'] = token
        cfg._save()


@wizard.command()
def prefixes():
    cfg._load()
    click.echo('Current prefixes:\n')
    for prefix in cfg['prefixes']:
        click.echo(prefix)
    if click.confirm('Would you like to enter new prefixes?\n'
                     'This will replace all current ones!\n'):
        cfg['prefixes'] = []
        prefix = click.prompt('Please enter the first prefix!\n')
        cfg['prefixes'].append(prefix)
        while click.confirm('Wanna add one more?\n'):
            prefix = click.prompt('Please enter another prefix!\n')
            cfg['prefixes'].append(prefix)
        cfg._save()


@wizard.command()
def cmdChannel():
    cfg._load()
    click.echo('Current default command channel: ' + str(cfg['defaultCmdCh']))
    if click.confirm('Would you like to change it?\n'):
        cmdCh = click.prompt('Please enter the new default command channel\'s ID!\n',
                             type=int)
        cfg['defaultCmdCh'] = cmdCh
        cfg._save()


@wizard.command()
def status():
    cfg._load()
    # TODO: This needs improving, some kind of pretty printing.
    print(cfg.cfgs)


if __name__ == '__main__':
    wizard()
