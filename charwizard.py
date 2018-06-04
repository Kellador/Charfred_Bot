import os
import importlib
import click
from utils.config import Config

botDir = os.path.dirname(os.path.realpath(__file__))

cfg = Config(f'{botDir}/configs/botCfg.json')


def _cogs():
    for dirpath, _, filenames in os.walk('cogs'):
        if '__' in dirpath:
            continue
        else:
            for filename in filenames:
                if filename.endswith('.py'):
                    yield filename, os.path.join(dirpath, filename[:-3])


def _nodes(nodes):
    for node in nodes:
        if not click.confirm(f'Edit permissions for: \"{node}\"?'):
            continue
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
        cfg['nodes'][node]['role'] = ""
        if click.confirm('Would you like to limit which roles are permitted\n'
                         f'to use {node} commands?'):
            role = click.prompt('Please enter the minimum Discord role that should\n'
                                f'be able to use {node} commands')
            cfg['nodes'][node]['role'] = role
        cfg['nodes'][node]['channels'] = []
        if click.confirm(f'Would you like to limit where {node} commands\n'
                         'are allowed, to specific channels?'):
            channels = click.prompt(f'Please enter all channel\' IDs where {node} commands\n'
                                    'are allowed, seperated by spaces only!\n').split()
            channels = list(map(int, channels))
            cfg['nodes'][node]['channels'] = channels
        cfg._save()


def _initcogs():
    click.echo('We\'ll set up the permission nodes for all currently '
               'installed cogs (extensions) now. If the cog defines '
               'checks for its functions then these checks will run '
               'against these permissions.\n'
               'For every permission node you will be asked to provide '
               'some information. It may take a while if there are a '
               'lot of permission nodes.\n'
               'So let\'s get started!')
    os.chdir(botDir)
    for cogname, _cog in _cogs():
        cog = importlib.import_module(_cog.replace('/', '.').replace('\\', '.'))
        nodes = getattr(cog, 'permissionNodes', None)
        if nodes is None:
            continue
        click.echo('Beginning setup for permission nodes defined for '
                   f'{cogname}!')
        _nodes(nodes)
        click.echo(f'Done with all permission nodes for {cogname}!')
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

        cfg['hook'] = ''
        if click.confirm('Charfred\'s Error Handler is capable of sending tracebacks for '
                         'otherwise uncaught exceptions to a Discord Webhook, for your '
                         'convenience, if a webhook url is specified!\n'
                         'Do you wish to specify a webhook url to enable this feature?'):
            hook_url = click.prompt('Please enter the webhook url now!\n')
            cfg['hook'] = hook_url

        cfg['nodes'] = {}
        cfg._save()
        click.confirm('Great! We\'ve reached the breakpoint! The absolute basics '
                      'have been set up. This next part is gonna a lot longer!\n'
                      'You wanna continue now?\n', abort=True)
        _initcogs()
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
        _initcogs()
        cfg._save()
        click.echo('Configs for Charfred saved!')


@nodes.command()
def update():
    os.chdir(botDir)
    for cogname, _cog in _cogs():
        cog = importlib.import_module(_cog.replace('/', '.').replace('\\', '.'))
        nodes = getattr(cog, 'permissionNodes', None)
        if nodes is None:
            continue
        if type(nodes) is dict:
            newNodes = {}
            for k, v in nodes.items():
                if k not in cfg['nodes']:
                    newNodes[k] = v
        else:
            newNodes = []
            for node in nodes:
                if node not in cfg['nodes']:
                    newNodes.append(node)
        if len(newNodes) > 0:
            _nodes(newNodes)
            click.echo(f'Done with all permission nodes for {cogname}!')
        else:
            click.echo(f'No new nodes found for {cogname}!')
    else:
        click.echo('Excellent, we\'re all done with the permission nodes now!')
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
            click.echo('Old entry for minimum role:\n' +
                       ' '.join(cfg['nodes'][node]['role']))
            if click.confirm('Would you like to limit which roles are permitted\n'
                             f'to use {node} commands?'):
                role = click.prompt('Please enter the minimum Discord role that should\n'
                                    f'be able to use {node} commands')
                cfg['nodes'][node]['role'] = role
            if click.confirm(f'Would you like to limit where {node} commands\n'
                             'are allowed, to specific channels?'):
                click.echo('Old entries:\n' +
                           ' '.join(cfg['nodes'][node]['channels']))
                cfg['nodes'][node]['channels'] = []
                channels = click.prompt(f'Please enter all channel\' IDs where {node} commands\n'
                                        'are allowed, seperated by spaces only!\n').split()
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
def hook():
    cfg._load()
    if 'hook' in cfg.keys() and cfg['hook'] is not None:
        click.echo('Currently specified webhook url:\n')
        click.echo(cfg['hook'])
    else:
        click.echo('A webhook url for exception reporting is not currently specified!')
    cfg['hook'] = ''
    if click.confirm('Would you like to enter a new webhook url?\n'):
        hook_url = click.prompt('Please enter the webhook url now!\n')
        cfg['hook'] = hook_url
        cfg._save()


@wizard.command()
def status():
    cfg._load()
    # TODO: This needs improving, some kind of pretty printing.
    print(cfg.cfgs)


if __name__ == '__main__':
    wizard()
