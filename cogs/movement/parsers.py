from re import match
from cogs.movement.functions import aliases, types_by_command, types_by_arg
from cogs.movement.util import SimError


def separate_commands(text):
    
    # States:
    # 0: Looking for a function
    # 1: Scanning for the opening parenthesis or whitespace
    # 2: Scanning for the closing parenthesis

    state = 0
    start = 0
    depth = 0
    player_commands = []

    for i in range(len(text)):
        char = text[i]

        if state == 0:
            if match(r'[\w_\|-]', char):
                start = i
                state = 1

        elif state == 1:
            if char == '(':
                depth = 1
                state = 2
            elif not match(r'[\w_\|-]', char):
                player_commands.append(text[start:i])
                state = 0

        elif state == 2:
            if char == '(':
                depth += 1
            if  char == ')':
                depth -= 1
                if depth == 0:
                    player_commands.append(text[start:i + 1])
                    state = 0

    # Handle unfinished parsing of argumentless commands
    if state == 1:
        player_commands.append(text[start:])
    
    return player_commands

def argumentatize_command(command):
    # Handle argumentless commands
    try:
        divider = command.index('(')
    except ValueError:
        return [[command.lower(), []]]

    args = []
    start = divider + 1
    depth = 0
    for i in range(divider + 1, len(command) - 1):
        char = command[i]
        if depth == 0 and char == ',':
            args.append(command[start:i].strip())
            start = i + 1
        elif char == '(':
            depth += 1
        elif char == ')':
            depth -= 1

    command_name = command[:divider].lower()
    args.append(command[start:-1].strip())

    if command_name in ('repeat', 'rep', 'r'):
        print(args[0])
        commands = separate_commands(args[0])
        commands_args = [single for command in commands for single in argumentatize_command(command)] * int(args[1])
    else:
        commands_args = [[command_name, args]]
    print(commands_args)

    return commands_args

def dictize_args(command, str_args):
    out = {}

    command_types = list(types_by_command[command].keys())

    positional_index = 0
    for arg in str_args:
        if match(r'^[\w_\|]* ?=', arg): # if keyworded arg
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name)
            arg_val = convert(command, arg_name, arg[divider + 1:].strip())
        elif positional_index < len(command_types): # if positional arg
            arg_name = command_types[positional_index]
            # arg_name = dealias_arg_name(arg_name)
            # if match(r'^mb\(.*\)$', arg_name) or match(r'^mathbot\(.*\)$', arg_name):
            #     arg_val = None
            # else:
            arg_val = convert(command, arg_name, arg)
            positional_index += 1
        else:
            continue

        out.update({arg_name: arg_val})
    
    return out

def dealias_arg_name(arg_name):
    arg_name = arg_name.lower()
    return aliases.get(arg_name, arg_name)

def convert(command, arg_name, val):
    if arg_name in types_by_command[command]:
        type = types_by_command[command][arg_name]
    elif arg_name in types_by_arg:
        type = types_by_arg[arg_name]
    else:
        raise SimError(f'Unknown argument `{arg_name}`')
    try:
        return type(val)
    except:
        raise SimError(f'Error in `{command.__name__}` converting `{val}` to type `{arg_name}:{type.__name__}`')