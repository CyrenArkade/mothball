from numpy import float32, int32, uint64
from math import atan2, degrees, sqrt, copysign, atan, asin, acos, sin
from inspect import signature
from functools import wraps
from types import MethodType
from evalidate import Expr, EvalException
import cogs.movement.parsers as parsers
from cogs.movement.utils import Function, SimError, fastmath_sin_table
from cogs.movement.player import Player

f64 = float
f32 = float32
i32 = int32
u64 = uint64
PI = 3.14159265358979323846

commands_by_name = {}
types_by_command = {}
aliases = {}
types_by_arg = {}

def register_arg(arg, type, new_aliases = []):
    types_by_arg[arg] = type
    for alias in new_aliases:
        aliases[alias] = arg

register_arg('duration', int, ['dur', 't'])
register_arg('rotation', f32, ['rot', 'r'])
register_arg('forward', f32)
register_arg('strafe', f32)
register_arg('slip', f32, ['s'])
register_arg('airborne', bool, ['air'])
register_arg('sprinting', bool, ['sprint'])
register_arg('sneaking', bool, ['sneak', 'sn'])
register_arg('jumping', bool, ['jump'])
register_arg('speed', int, ['spd'])
register_arg('slowness', int, ['slow', 'sl'])
register_arg('soulsand', int, ['ss'])

def command(name=None, aliases=[]):
    def deco(f):
        nonlocal name, aliases

        @wraps(f)
        def wrapper(*args, **kwargs):
            args = list(args)
            for k, v in f._defaults.items():
                if v == None:
                    args.append(args[0].get(k))
                    continue
                args[0].setdefault(k, v)
                args.append(args[0].get(k))
            return f(*args, **kwargs)

        params = signature(wrapper).parameters
        defaults = []
        arg_types = []
        for k, v in list(params.items())[1:]:
            defaults.append((k, v.default))
            arg_types.append((k, v.annotation if v.default is None else type(v.default)))
        f._defaults = dict(defaults)
        types_by_command[wrapper] = dict(arg_types)
        
        if name is None:
            name = wrapper.__name__
        commands_by_name[name] = wrapper
        wrapper._aliases = [name] + aliases
        for alias in aliases:
            commands_by_name[alias] = wrapper
        
        return wrapper
    return deco


def move(args):
    for _ in range(abs(args['duration'])):
        args['player'].move(args)

def jump(args, after_jump_tick = lambda: None):
    
    args['jumping'] = True
    args['player'].move(args)
    args['jumping'] = False

    after_jump_tick()
    
    args.setdefault('airborne', True)
    for i in range(abs(args['duration']) - 1):
        args['player'].move(args)


@command(aliases=['rep', 'r'])
def repeat(args, inputs = '', n = 1):
    commands_args = parsers.string_to_args(inputs)

    for _ in range(n):
        for command, cmd_args in commands_args:
            parsers.execute_command(args['envs'], args['player'], command, cmd_args)

@command(aliases=['def'])
def define(args, name = '', input = ''):

    dictized = parsers.string_to_args(input)
    new_function = Function(name, dictized, args['pos_args'])

    lowest_env = args['envs'][-1]
    lowest_env[name] = new_function

@command()
def var(args, name = '', input = ''):
    lowest_env = args['envs'][-1]
    try:
        local_env = {}
        for env in args['envs']:
            local_env.update(env)
        input = parsers.safe_eval(input, local_dict=local_env)
    except:
        pass
    lowest_env[name] = input


@command(aliases=['sn'])
def sneak(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    move(args)

@command(aliases=['sns'])
def sneaksprint(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('sprinting', True)
    move(args)

@command(aliases=['w'])
def walk(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    move(args)

@command(aliases=['s'])
def sprint(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    move(args)

@command(aliases=['sn45'])
def sneak45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    move(args)

@command(aliases=['sns45'])
def sneaksprint45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('sprinting', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    move(args)

@command(aliases=['w45'])
def walk45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    move(args)

@command(aliases=['s45'])
def sprint45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    move(args)

@command(aliases=['sna'])
def sneakair(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['snsa'])
def sneaksprintair(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('sprinting', True)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['wa'])
def walkair(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['sa'])
def sprintair(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['sneakair45', 'sn45a', 'sna45'])
def sneak45air(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['sneaksprintair45', 'sns45a', 'snsa45'])
def sneaksprint45air(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['walkair45', 'w45a', 'wa45'])
def walk45air(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['sprintair45', 's45a', 'sa45'])
def sprint45air(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['snj'])
def sneakjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    jump(args)

@command(aliases=['snsj'])
def sneaksprintjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('sprinting', True)
    jump(args)

@command(aliases=['wj'])
def walkjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    jump(args)

@command(aliases=['lwj'])
def lwalkjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))

    def update():
        args['strafe'] = f32(0)

    jump(args, after_jump_tick = update)

@command(aliases=['rwj'])
def rwalkjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(-1))

    def update():
        args['strafe'] = f32(0)

    jump(args, after_jump_tick = update)

@command(aliases=['sj'])
def sprintjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    jump(args)

@command(aliases=['lsj'])
def lsprintjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))
    args.setdefault('sprinting', True)

    def update():
        args['strafe'] = f32(0)

    jump(args, after_jump_tick = update)

@command(aliases=['rsj'])
def rsprintjump(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(-1))
    args.setdefault('sprinting', True)

    def update():
        args['strafe'] = f32(0)

    jump(args, after_jump_tick = update)

@command(aliases=['snj45'])
def sneakjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    jump(args)

@command(aliases=['snsj45'])
def sneaksprintjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('sprinting', True)
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    jump(args)

@command(aliases=['wj45'])
def walkjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))
    args['function_offset'] = f32(45)
    jump(args)

@command(aliases=['sj45'])
def sprintjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('sprinting', True)
    
    def update():
        args.setdefault('strafe', f32(1))
        args['function_offset'] = f32(45)
    
    jump(args, after_jump_tick = update)

@command(aliases=['lsj45'])
def lsprintjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(1))
    args.setdefault('sprinting', True)
    
    args['function_offset'] = f32(45)
    
    jump(args)

@command(aliases=['rsj45'])
def rsprintjump45(args, duration = 1, rotation: f32 = None):
    args.setdefault('forward', f32(1))
    args.setdefault('strafe', f32(-1))
    args.setdefault('sprinting', True)
    
    args['function_offset'] = f32(-45)
    
    jump(args)

@command(aliases=['snp'])
def sneakpessi(args, duration = 1, delay = 1, rotation: f32 = None):

    args['duration'] = delay
    jump(args)

    args['duration'] = duration - delay
    args.setdefault('forward', f32(1))
    args.setdefault('sneaking', True)
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['wp'])
def walkpessi(args, duration = 1, delay = 1, rotation: f32 = None):

    args['duration'] = delay
    jump(args)

    args['duration'] = duration - delay
    args.setdefault('forward', f32(1))
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['sp'])
def sprintpessi(args, duration = 1, delay = 1, rotation: f32 = None):

    args['duration'] = delay
    jump(args)

    def update():
        args['sprinting'] = True

    args['duration'] = duration - delay
    args.setdefault('forward', f32(1))
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['st'])
def stop(args, duration = 1):
    move(args)

@command(aliases=['sta'])
def stopair(args, duration = 1):
    args.setdefault('airborne', True)
    move(args)

@command(aliases=['stj'])
def stopjump(args, duration = 1):
    jump(args)

@command(name='|')
def reset_position(args):
    args['player'].x = 0
    args['player'].modx = 0
    args['player'].z = 0
    args['player'].modz = 0

@command(name='b')
def dist_to_blocks(args):
    if args['player'].x > 0:
        args['player'].modx += f32(0.6)
    elif args['player'].x < 0:
        args['player'].modx -= f32(0.6)

    if args['player'].z > 0:
        args['player'].modz += f32(0.6)
    elif args['player'].z < 0:
        args['player'].modz -= f32(0.6)

@command(name='mm')
def dist_to_mm(args):
    if args['player'].x > 0:
        args['player'].modx -= f32(0.6)
    elif args['player'].x < 0:
        args['player'].modx += f32(0.6)

    if args['player'].z > 0:
        args['player'].modz -= f32(0.6)
    elif args['player'].z < 0:
        args['player'].modz += f32(0.6)

@command(aliases=['$'])
def zero(args):
    args['player'].modx -= args['player'].x
    args['player'].modz -= args['player'].z

@command()
def zerox(args):
    args['player'].modx -= args['player'].x

@command()
def zeroz(args):
    args['player'].modz -= args['player'].z

@command(aliases = ['v'])
def setv(args, vx = 0.0, vz = 0.0):
    args['player'].vx = vx
    args['player'].vz = vz

@command(aliases = ['vx'])
def setvx(args, vx = 0.0):
    args['player'].vx = vx

@command(aliases = ['vz'])
def setvz(args, vz = 0.0):
    args['player'].vz = vz

@command(aliases = ['pos', 'xz'])
def setpos(args, x = 0.0, z = 0.0):
    args['player'].x = x
    args['player'].z = z

@command(aliases = ['posx', 'x'])
def setposx(args, x = 0.0):
    args['player'].x = x

@command(aliases = ['posz', 'z'])
def setposz(args, z = 0.0):
    args['player'].z = z

@command()
def speed(args, speed = 0):
    args['player'].speed = speed

@command(aliases = ['slow'])
def slowness(args, slowness = 0):
    args['player'].slowness = slowness

@command(aliases = ['slip'])
def setslip(args, slip = f32(0)):
    args['player'].ground_slip = slip

@command(aliases = ['a'])
def angles(args, angles = -1):
    args['player'].angles = angles

@command()
def inertia(args, inertia = 0.005):
    args['player'].inertia_threshold = inertia

@command(aliases = ['pre'])
def precision(args, precision = 6):
    args['player'].printprecision = precision

@command(aliases = ['facing', 'face', 'f'])
def rotation(args, angle = f32(0)):
    args['player'].default_rotation = angle

@command(aliases = ['offrotation', 'or', 'offsetfacing', 'of'])
def offsetrotation(args, angle = f32(0)):
    args['player'].rotation_offset = angle

@command(aliases = ['turn'])
def turn(args, angle = f32(0)):
    args['player'].default_rotation += angle

@command(aliases = ['ssand', 'ss'])
def soulsand(args, soulsand = 1):
    args['player'].soulsand = soulsand

@command(aliases = ['aq', 'qa'])
def anglequeue(args):
    def to_f32(val):
        try:
            return f32(val)
        except:
            raise SimError(f'Error in `anglequeue` converting `{val}` to type `rotation:float32`')
    args['player'].rotation_queue.extend(map(to_f32, args['pos_args']))

@command(aliases = ['tq', 'qt'])
def turnqueue(args):
    def to_f32(val):
        try:
            return f32(val)
        except:
            raise SimError(f'Error in `turnqueue` converting `{val}` to type `rotation:float32`')
    args['player'].turn_queue.extend(map(to_f32, args['pos_args']))

@command()
def macro(args, name = 'macro'):
    args['player'].macro = name

@command()
def outx(args):
    args['player'].out += f"X: {args['player'].format(args['player'].x)}\n"
@command()
def outz(args):
    args['player'].out += f"Z: {args['player'].format(args['player'].z)}\n"

@command()
def outvx(args):
    args['player'].out += f"Vx: {args['player'].format(args['player'].vx)}\n"
@command()
def outvz(args):
    args['player'].out += f"Vz: {args['player'].format(args['player'].vz)}\n"

@command(name='outxmm', aliases=['xmm'])
def x_mm(args):
    args['player'].out += f"X mm: {args['player'].format(args['player'].x + (-f32(0.6) if args['player'].x > 0 else f32(0.6)))}\n"
@command(name='outzmm', aliases=['zmm'])
def z_mm(args):
    args['player'].out += f"Z mm: {args['player'].format(args['player'].z + (-f32(0.6) if args['player'].z > 0 else f32(0.6)))}\n"

@command(name='outxb', aliases=['xb'])
def x_b(args):
    args['player'].out += f"X b: {args['player'].format(args['player'].x - (-f32(0.6) if args['player'].x > 0 else f32(0.6)))}\n"
@command(name='outzb', aliases=['zb'])
def z_b(args):
    args['player'].out += f"Z b: {args['player'].format(args['player'].z - (-f32(0.6) if args['player'].z > 0 else f32(0.6)))}\n"
    
@command(aliases = ['speedvec', 'vector', 'vec'])
def speedvector(args):
    angle = degrees(atan2(-args['player'].vx, args['player'].vz))
    speed = sqrt(args['player'].vx**2 + args['player'].vz**2)
    args['player'].out += f"Angle: {args['player'].format(angle)}\n"
    args['player'].out += f"Speed: {args['player'].format(speed)}\n"

@command(aliases = ["poss"])
def possibilities(args, inputs = 'sj45(100)', mindistance = 0.01, offset = f32(0.6)):
    
    player = args['player']
    format = player.format
    old_move = player.move

    tick = 1
    def move(self, args):
        nonlocal tick, old_move

        old_move(args)

        player_blocks = player.z + offset
        jump_pixels = int(player_blocks / 0.0625)
        jump_blocks = jump_pixels * 0.0625
        poss_by = player_blocks - jump_blocks

        if poss_by < mindistance:
            player.out += f'Tick {tick}: {format(poss_by)} ({format(jump_blocks)}b)\n'
        
        tick += 1
    
    player.out += '```'
    player.move = MethodType(move, player)
    
    commands_args = parsers.string_to_args(inputs)
    for command, cmd_args in commands_args:
        parsers.execute_command(args['envs'], player, command, cmd_args)
    
    player.out += '```'
    player.move = old_move

@command(aliases=['ji'])
def jumpinfo(args, x = 0.0, z = 0.0):

    player = args['player']

    if abs(x) < 0.6:
        dx = 0.0
    else:
        dx = x - copysign(0.6, x)
    if abs(z) < 0.6:
        dz = 0.0
    else:
        dz = z - copysign(0.6, z)
    
    if dx == 0.0 and dz == 0.0:
        player.out += 'That\'s not a jump!'
        return
    elif dx == 0.0 or dz == 0.0:
        player.out +=  f'**{player.format(max(x, z))}b** jump -> **{player.format(max(dx, dz))}** distance'
        return

    distance = sqrt(dx**2 + dz**2)
    angle = degrees(atan(dz/dx))

    lines = [
        f'A **{player.format(x)}b** by **{player.format(z)}b** block jump:',
        f'Dimensions: **{player.format(dx)}** by **{player.format(dz)}**',
        f'Distance: **{player.format(distance)}** distance -> **{player.format(distance+0.6)}b** jump',
        f'Optimal Angle: **{angle:.3f}°**'
    ]

    player.out += '\n'.join(lines) + '\n'

@command()
def duration(args, floor = 0.0, ceiling = 0.0, inertia = 0.005, jump_boost = 0):

    player = args['player']
    vy = 0.42 + 0.1 * jump_boost
    y = 0
    ticks = 0

    while y > floor or vy > 0:
        y = y + vy
        if ceiling != 0.0 and y > ceiling - 1.8:
            y = ceiling - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < inertia:
            vy = 0
        ticks += 1

        if ticks > 5000:
            player.out += 'Simulation limit reached.'
            return

    if vy >= 0:
        player.out += 'Impossible jump height. Too high.'
        return

    ceiling = f' {ceiling}bc' if ceiling != 0.0 else ''
    player.out += f'Duration of a {floor}b{ceiling} jump:\n**{ticks} ticks**'

@command()
def height(args, duration = 12, ceiling = 0.0, inertia = 0.005, jump_boost = 0):

    player = args['player']
    vy = 0.42 + jump_boost * 0.1
    y = 0

    for i in range(duration):
        y = y + vy
        if ceiling != 0.0 and y > ceiling - 1.8:
            y = ceiling - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < inertia:
            vy = 0

        if i > 5000:
            player.out += ('Simulation limit reached.')
            return
    
    ceiling = f' with a {ceiling}bc' if ceiling != 0.0 else ''
    player.out += (f'Height after {duration} ticks{ceiling}:\n**{round(y, 6)}**')

@command()
def blip(args, blips = 1, blip_height = 0.0625, init_height: f64 = None, init_vy: f64 = None, inertia = 0.005, jump_boost = 0):

    if init_height is None:
        init_height = blip_height
    if init_vy is None:
        init_vy = 0.42 + 0.1 * jump_boost    
    
    player = player = args['player']
    blips_done = 0
    vy = init_vy
    y = init_height
    jump_ys = [init_height]
    max_heights = []
    vy_prev = 0
    i = 0

    while blips_done < blips or vy > 0:

        y += vy
        vy = (vy - 0.08) * 0.98

        if y + vy < blip_height:

            if y + vy > 0:
                max_heights.append('Fail')
                jump_ys.append(y + vy)
                break
            
            jump_ys.append(y)
            vy = 0.42
            blips_done += 1
        
        if abs(vy) < inertia:
            vy = 0

        if vy_prev > 0 and vy <= 0:
            max_heights.append(y)

        if i > 5000:
            player.out += 'Simulation limit reached.'
            return

        vy_prev = vy
        i += 1

    out = '\n'.join([
        f'Blips: {blips_done}',
        f'Blip height: {round(blip_height, 6)}',
        f'Initial y: {round(init_height, 6)}',
        f'Initial vy: {round(init_vy, 6)}',
        f'```Blip | Jumped From | Max Height'
    ])

    num_col_width = len(str(blips))
    for i in range(0, len(jump_ys)):
        num = f'{i:0{num_col_width}}'.ljust(4)
        jumped_from = f'{jump_ys[i]:<11.6f}'
        max_height = f'{max_heights[i]:<10.6f}' if type(max_heights[i]) == f64 else max_heights[i]
        out += (f'\n{num} | {jumped_from} | {max_height}')
    out += '```'
    
    player.out += out

@command()
def bwmm(args, mm = 1.0, strat = 'sj45(12)'):
    player = args['player']

    p1 = player.softcopy()
    p1.vz = 0.0
    p1.inertia = 0.0
    parsers.execute_string(strat, args['envs'], p1)

    p2 = player.softcopy()
    p2.inertia = 0.0
    p2.vz = 1.0 * mm
    parsers.execute_string(strat, args['envs'], p2)

    speed = (p1.z - mm + (f32(0.6) if mm < 0 else -f32(0.6))) / (p1.z - p2.z) * mm
    player.vz = speed
    parsers.execute_string(strat, args['envs'], player)
    player.pre_out += f'Speed: {player.format(speed)}\n'
    player.pre_out += f'MM: {player.format(player.z + (f32(0.6) if player.z < 0 else -f32(0.6)))}\n'

@command()
def inv(args, goal = 1.6, strat = 'sj45(12)'):
    player = args['player']

    p1 = player.softcopy()
    p1.inertia = 0.0
    p1.vz = 0.0
    parsers.execute_string(strat, args['envs'], p1)
    p1_dist = p1.z

    p2 = player.softcopy()
    p2.inertia = 0.0
    p2.vz = 1.0 * goal
    parsers.execute_string(strat, args['envs'], p2)
    p2_dist = p2.z

    speed = (p1_dist - goal) / (p1_dist - p2_dist) * goal
    player.vz = speed
    parsers.execute_string(strat, args['envs'], player)
    player.pre_out += f'Speed: {player.format(speed)}\n'
    player.pre_out += f'Dist: {player.format(player.z)}\n'

@command()
def speedreq(args, blocks = 5.0, strat = 'sj45(12)'):
    player = args['player']

    p1 = player.softcopy()
    p1.inertia = 0.0
    p1.vz = 0.0
    parsers.execute_string(strat, args['envs'], p1)
    p1_blocks = p1.z

    p2 = player.softcopy()
    p2.inertia = 0.0
    p2.vz = 1.0 * blocks
    parsers.execute_string(strat, args['envs'], p2)
    p2_blocks = p2.z

    speed = (p1_blocks - blocks + (f32(0.6) if blocks > 0 else -f32(0.6))) / (p1_blocks - p2_blocks) * blocks
    player.vz = speed
    parsers.execute_string(strat, args['envs'], player)
    player.pre_out += f'Speed: {player.format(speed)}\n'
    player.pre_out += f'Blocks: {player.format(player.z + (f32(0.6) if player.z > 0 else -f32(0.6)))}\n'

@command(aliases=['angle'])
def angleinfo(args, angle = f32(0.0), mode = 'vanilla'):

    angle_rad = angle * f32(PI) / f32(180)

    if mode == 'vanilla':
        sin_index = u64(i32(angle_rad * f32(10430.378)) & 65535)
        cos_index = u64(i32(angle_rad * f32(10430.378) + f32(16384.0)) & 65535)
        sin_value = sin(sin_index * PI * 2.0 / 65536)
        cos_value = sin(cos_index * PI * 2.0 / 65536)
        cos_index_adj = (int(cos_index) - 16384) % 65536
    elif mode == 'optifine':
        sin_index = u64(i32(angle_rad * f32(651.8986)) & 4095)
        cos_index = u64(i32((angle_rad + f32(1.5707964)) * f32(651.8986)) & 4095)
        sin_value = fastmath_sin_table[sin_index]
        cos_value = fastmath_sin_table[cos_index]
        cos_index_adj = (int(cos_index) - 1024) % 4096
    else:
        raise SimError(f'Unkown mode {mode}. Options are `vanilla`, `optifine`')
    
    sin_angle = degrees(asin(sin_value))
    cos_angle = degrees(acos(cos_value))
    normal = sqrt(sin_value**2.0 + cos_value**2.0)

    format = args['player'].format
    output = [
        [f'{format(angle)}°', 'Sin', 'Cos', 'Normal'],
        ['Value', format(sin_value), format(cos_value), format(normal)],
        ['Angle', format(sin_angle), format(cos_angle), ''],
        ['Index', format(sin_index), f'{format(cos_index_adj)} ({format(cos_index)})', '']
    ]

    for col in output:
        col_width = max(map(len, col)) + 2
        for i in range(len(col)):
            col[i] = col[i].ljust(col_width)

    args['player'].out += '```'
    for i in range(4):
        for j in range(4):
            args['player'].out += output[j][i]
        args['player'].out += '\n'
    args['player'].out += '```'

@command()
def help(args, cmd_name = 'help'):
    if cmd_name not in commands_by_name:
        args['player'].out += f'`{cmd_name}` not found\n'
        return

    cmd = commands_by_name[cmd_name]
    cmd_name = cmd._aliases[0]
    params = []
    for k, v in list(signature(cmd).parameters.items())[1:]:
        out = '  '
        out += k
        anno_type = v.annotation if v.default is None else type(v.default)
        out += f": {anno_type.__name__}"
        out += " = " + (str(v.default) if anno_type != str else f'"{v.default}"')
        params.append(out)
    newln = '\n'
    # args['player'].out += f'{cmd_name} Help:```\nAliases:\n{(newln+"  ").join(cmd._aliases)}\nArgs:\n{newln.join(params)}```\n'
    args['player'].out += f'Help with {cmd_name}:```\n'
    args['player'].out += f'Aliases:\n{newln.join(map(lambda x: "  "+x, cmd._aliases))}\n'
    args['player'].out += f'Args:\n{newln.join(params)}```\n'