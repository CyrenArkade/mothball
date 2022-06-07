player_commands = {}
player_command_args = {}

def player_command(name=None, aliases=[], arguments=[]):

    def inner(f):

        nonlocal name, aliases, arguments

        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        
        if name is None:
            name = f.__name__

        player_commands.update({name: f})

        for alias in aliases:
            player_commands.update({alias: f})
        
        player_command_args.update({f: arguments})
        
        return wrapper
    return inner

def get_player_commands():
    return player_commands

def get_player_command_args():
    return player_command_args

def get_player_arg_aliases():
    all_aliases = {}
    add_alias = lambda arg, aliases: [all_aliases.update({alias: arg}) for alias in aliases]

    add_alias('duration', ['dur', 't'])
    add_alias('direction', ['dir', 'd'])
    add_alias('facing', ['face', 'f'])
    add_alias('slip', ['s'])
    add_alias('airborne', ['air'])
    add_alias('mov_mult', ['movmult', 'mov', 'm'])
    add_alias('eff_mult', ['effmult', 'eff', 'e'])
    add_alias('sprintjump_tick', ['sprintjump'])
    add_alias('slowness', ['slow', 'sl'])
    add_alias('speed', ['sp', 'spd'])

    return all_aliases