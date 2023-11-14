from re import match, search
import cogs.movement.functions as functions
from cogs.movement.utils import SimError
from numpy import float32 as fl
from evalidate import Expr, base_eval_model

if 'USub' not in base_eval_model.nodes:
    base_eval_model.nodes.append('USub')
    base_eval_model.nodes.append('UAdd')
    base_eval_model.nodes.append('Mult')
    base_eval_model.nodes.append('FloorDiv')
    base_eval_model.nodes.append('Pow')

def execute_string(text, envs, player):
    commands_args = string_to_args(text)
    for command, args in commands_args:
        execute_command(envs, player, command, args)
    
def string_to_args(text):
    commands_str_list = separate_commands(text)
    commands_args = [argumentatize_command(command) for command in commands_str_list]
    return commands_args

def execute_command(envs, player, command, args):

    # Handle command modifiers
    modifiers = {}
    if command.startswith('-'):
        command = command[1:]
        modifiers['reverse'] = True
    
    if command.endswith('.land'):
        command = command[:-5]
        modifiers['prev_slip'] = fl(1.0)
    
    key_modifier = search(r'\.([ws]?[ad]?){1,2}(\.|$)', command)
    if key_modifier:
        keys = key_modifier.group(0)[1:]

        if 'w' in keys: modifiers.setdefault('forward', fl(1))
        if 's' in keys: modifiers.setdefault('forward', fl(-1))
        if 'a' in keys: modifiers.setdefault('strafe', fl(1))
        if 'd' in keys: modifiers.setdefault('strafe', fl(-1))

        modifiers.setdefault('forward', fl(0))
        modifiers.setdefault('strafe', fl(0))

        command = command.replace(key_modifier.group(0), '', 1)
    # End handling command modifiers

    
    if command in commands_by_name: # Normal execution
        command_function = commands_by_name[command]

        dict_args = dictize_args(envs, command_function, args)
        dict_args.update(modifiers)
        dict_args['player'] = player
        dict_args['envs'] = envs

        command_function(dict_args)

    else: # CommandNotFound or user-defined function
        user_func = fetch(envs, command)
        
        if user_func is None:
            raise SimError(f'Command `{command}` not found')
        
        new_env = dict([(var, val) for var, val in zip(user_func.arg_names, args)])

        for command, args in user_func.args:
            execute_command(envs + [new_env], player, command, args)



def separate_commands(text):
    
    # States:
    # 0: Looking for a function
    # 1: Scanning for the opening parenthesis or whitespace
    # 2: Scanning for the closing parenthesis
    # 3: In a comment

    state = 0
    comment_state = None
    start = 0
    depth = 0
    player_commands = []

    for i in range(len(text)):
        char = text[i]

        if char == '#':
            if state != 3:
                comment_state = state
                state = 3
            else:
                state = comment_state
            continue

        if state == 0:
            if match(r'[\w_\|\-\.]', char):
                start = i
                state = 1

        elif state == 1:
            if char == '(':
                depth = 1
                state = 2
            elif not match(r'[\w_\|\-\.]', char):
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
    elif state == 2:
        raise SimError('Unmatched opening parenthesis')

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
    final_arg = command[start:-1].strip()
    if len(final_arg) > 0:
        args.append(final_arg)

    return (command_name, args)

def dictize_args(envs, command, str_args):
    out = {}
    out.setdefault('pos_args', [])

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
            out['pos_args'].append(arg)
            continue

        out[arg_name] = arg_val
    
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
        return cast(envs, type, val) # if normal value
    except:
        raise SimError(f'Error in `{command.__name__}` converting `{val}` to type `{arg_name}:{type.__name__}`')

def cast(envs, type, val):
    if type == bool:
        return val.lower() not in ('f', 'false', 'no', 'n', '0')
    if val.lower() in ('none', 'null'):
        return None
    if type in (int, float, fl):
        local_env = {}
        for env in envs:
            local_env.update(env)
        for k, v in local_env.items():
            try:
                local_env[k] = type(v)
            except:
                continue
        return type(safe_eval(val, local_env))
    else:
        return type(val)

def fetch(envs, name):
    for env in envs[::-1]:
        if name in env:
            return env[name]

def safe_eval(val, env):
    return Expr(val.replace('^', '**'), model=base_eval_model).eval(env)

aliases = functions.aliases
commands_by_name = functions.commands_by_name
types_by_command = functions.types_by_command
types_by_arg = functions.types_by_arg