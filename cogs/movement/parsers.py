from re import match
import cogs.movement.functions as functions
from cogs.movement.utils import SimError

def execute_string(text, envs, player):
    commands_args = string_to_args(text)
    execute_args(commands_args, envs, player)
    
def string_to_args(text):
    commands_str_list = separate_commands(text)
    commands_args = [argumentatize_command(command) for command in commands_str_list]
    return commands_args

def execute_args(commands_args, envs, player):
    for command, args in commands_args:
        reverse = command.startswith('-')
        if reverse:
            command = command[1:]
        
        if command in commands_by_name: # Normal execution
            command_function = commands_by_name[command]

            dict_args = dictize_args(envs, command_function, args)
            if reverse:
                dict_args.update({'reverse': True})
            dict_args.update({'player': player})
            dict_args.update({'envs': envs})

            command_function(dict_args)

        else: # CommandNotFound or user-defined function
            user_func = fetch(envs, command)
            
            if user_func is None:
                raise SimError(f'Command `{command}` not found')
            
            new_env = dict([(var, val) for var, val in zip(user_func.arg_names, args)])

            execute_args(user_func.args, envs + [new_env], player)



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
        return (command.lower(), [])

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

    return (command_name, args)

def dictize_args(envs, command, str_args):
    out = {}

    command_types = list(types_by_command[command].keys())

    positional_index = 0
    for arg in str_args:
        if match(r'^[\w_\|]* ?=', arg): # if keyworded arg
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name)
            arg_val = convert(envs, command, arg_name, arg[divider + 1:].strip())

        elif positional_index < len(command_types): # if positional arg
            arg_name = command_types[positional_index]
            arg_val = convert(envs, command, arg_name, arg)
            positional_index += 1

        else: # extra positional args
            out.setdefault('pos_args', [])
            out['pos_args'].append(arg)

        out.update({arg_name: arg_val})
    
    return out

def dealias_arg_name(arg_name):
    arg_name = arg_name.lower()
    return aliases.get(arg_name, arg_name)

def convert(envs, command, arg_name, val):
    if arg_name in types_by_command[command]: # if positionial arg
        type = types_by_command[command][arg_name]
    elif arg_name in types_by_arg: # if keyworded arg
        type = types_by_arg[arg_name]
    else:
        raise SimError(f'Unknown argument `{arg_name}`')
    try:
        return type(val) # if normal value
    except:
        fetched = fetch(envs, val)
        
        if fetched is not None:
            return type(fetched) # if variable

        # THIS IS AN AWFUL SOLUTION PLEASE CHANGE LATER
        # EVERYTHING ABOUT THIS IS TERRIBLE BUT I'M LAZY
        if arg_name == 'rotation' and match(r'^([ws]?[ad]?){1,2}$', val):
            print(val)
            if val == 'w':
                return type(0.0)
            elif val == 'a':
                return type(-90.0)
            elif val == 's':
                return type(180.0)
            elif val == 'd':
                return type(90.0)
            elif 'w' in val and 'd' in val:
                return type(45.0)
            elif 'w' in val and 'a' in val:
                return type(-45.0)
            elif 's' in val and 'd' in val:
                return type(135.0)
            elif 's' in val and 'a' in val:
                return type(-135.0)

        raise SimError(f'Error in `{command.__name__}` converting `{val}` to type `{arg_name}:{type.__name__}`')

def fetch(envs, name):
    for env in envs[::-1]:
        if name in env:
            return env[name]

aliases = functions.aliases
commands_by_name = functions.commands_by_name
types_by_command = functions.types_by_command
types_by_arg = functions.types_by_arg