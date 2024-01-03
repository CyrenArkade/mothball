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

def execute_string(context, text):

    try:
        commands_args = string_to_args(text)
    except SimError:
        raise
    except Exception:
        if context.is_dev:
            raise
        raise SimError('Something went wrong while parsing.')

    for command, args in commands_args:

        try:
            execute_command(context, command, args)
        except SimError:
            raise
        except Exception:
            if context.is_dev:
                raise
            raise SimError(f'Something went wrong while executing `{command}`.')
    
def string_to_args(text):
    commands_str_list = separate_commands(text)
    commands_args = [argumentatize_command(command) for command in commands_str_list]
    return commands_args

def execute_command(context, command, args):

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

        context.args, context.pos_args = dictize_args(context.envs, command_function, args)
        context.args.update(modifiers)

        command_function(context)

    else: # CommandNotFound or user-defined function
        user_func = fetch(context.envs, command)
        
        if user_func is None:
            raise SimError(f'Command `{command}` not found')
        
        new_env = dict([(var, val) for var, val in zip(user_func.arg_names, args)])

        for command, args in user_func.args:
            context.envs.append(new_env)
            execute_command(context, command, args)
            context.envs.pop()



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
    args = {}
    pos_args = []

    command_types = list(types_by_command[command].keys())

    positional_index = 0
    for arg in str_args:
        if match(r'^[\w_\|]* ?=', arg): # if keyworded arg
            divider = arg.index('=')
            arg_name = arg[:divider].strip()
            arg_name = dealias_arg_name(arg_name)
            arg_val = convert(envs, command, arg_name, arg[divider + 1:].strip())
            args[arg_name] = arg_val

        elif positional_index < len(command_types): # if positional arg
            arg_name = command_types[positional_index]
            arg_val = convert(envs, command, arg_name, arg)
            positional_index += 1
            args[arg_name] = arg_val
        
        pos_args.append(arg)
    
    return args, pos_args

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