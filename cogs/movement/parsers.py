from re import match
from ast import arg, literal_eval
import cogs.movement.commandmanager as cmdmgr

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
            if match(r'[\w_\|]', char):
                start = i
                state = 1

        elif state == 1:
            if char == '(':
                depth = 1
                state = 2
            elif not match(r'[\w_\|]', char):
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
        return [(command.lower(), [])]

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
        commands = separate_commands(args[0])
        comamnds_args = [single for command in commands for single in argumentatize_command(command)] * int(args[1])
    else:
        comamnds_args = [(command_name, args)]

    if len(comamnds_args) > 100000:
        return []

    return comamnds_args

def dictize_args(command_args, positional_args):
    out = {}

    positional_index = 0
    mathbot_updates = []
    for arg in command_args:
        if match(r'^[\w_\|]* ?=', arg): # if arg assigns
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name)
            arg_val = convert(arg[divider + 1:].strip())
        elif not positional_index >= len(positional_args): # if arg is positional
            arg_name = positional_args[positional_index]
            arg_name = dealias_arg_name(arg_name)
            if match(r'^mb\(.*\)$', arg_name) or match(r'^mathbot\(.*\)$', arg_name):
                arg_val = None
                #update = lambda x: out.update({arg_name: convert(x)}) # CHANGE THIS
                #mathbot_updates.append(update)
                pass
            else:
                arg_val = convert(arg)
            positional_index += 1
        else:
            continue

        out.update({arg_name: arg_val})
    
    return out, mathbot_updates

def dealias_arg_name(arg_name):
    arg_name = arg_name.lower()
    return cmdmgr.get_player_arg_aliases().get(arg_name, arg_name)

def convert(n):
    val = literal_eval(n)
    if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
        return int(val)
    return val