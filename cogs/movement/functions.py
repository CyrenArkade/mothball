import math
from numpy import float32 as fl
from inspect import signature, Parameter
from functools import wraps

commands_by_name = {}
types_by_command = {}
aliases = {}

add_alias = lambda arg, newaliases: [aliases.update({alias: arg}) for alias in newaliases]

add_alias('duration', ['dur', 't'])
add_alias('rotation', ['rot', 'r'])
add_alias('slip', ['s'])
add_alias('airborne', ['air'])
add_alias('mov_mult', ['movmult', 'mov', 'm'])
add_alias('eff_mult', ['effmult', 'eff', 'e'])
add_alias('sprinting', ['sprint'])
add_alias('sneaking', ['sneak', 'sn'])
add_alias('jumping', ['jump'])
add_alias('speed', ['sp', 'spd'])
add_alias('slowness', ['slow', 'sl'])

def command(name=None, aliases=[]):
    def inner(f):
        nonlocal name, aliases

        @wraps(f)
        def wrapper(*args, **kwargs):
            args = list(args)
            for k, v in f._defaults.items():
                if v == None:
                    continue
                args[1].setdefault(k, v)
                args.append(args[1].get(k))
            return f(*args, **kwargs)

        params = signature(wrapper).parameters
        defaults = []
        arg_types = []
        for k, v in list(params.items())[2:]:
            defaults.append((k, v.default))
            arg_types.append((k, v.annotation if v.default is None else type(v.default)))
        f._defaults = dict(defaults)
        types_by_command.update({wrapper: dict(arg_types)})
        
        if name is None:
            name = wrapper.__name__
        commands_by_name.update({name: wrapper})
        for alias in aliases:
            commands_by_name.update({alias: wrapper})
        
        return wrapper
    return inner


def move(player, args):
    for _ in range(abs(args['duration'])):
        player.move(args)

def jump(player, args, after_jump_tick = lambda: None):
    
    args['jumping'] = True
    player.move(args)
    args['jumping'] = False

    after_jump_tick()
    
    args.setdefault('airborne', True)
    for i in range(abs(args['duration']) - 1):
        player.move(args)


@command(aliases=['sn'])
def sneak(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    move(player, args)

@command(aliases=['w'])
def walk(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    move(player, args)

@command(aliases=['s'])
def sprint(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    move(player, args)

@command(aliases=['sn45'])
def sneak45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    move(player, args)

@command(aliases=['w45'])
def walk45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    move(player, args)

@command(aliases=['s45'])
def sprint45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    move(player, args)

@command(aliases=['sna'])
def sneakair(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['wa'])
def walkair(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['sa'])
def sprintair(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['sneakair45', 'sn45a', 'sna45'])
def sneak45air(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['walkair45', 'w45a', 'wa45'])
def walk45air(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['sprintair45', 's45a', 'sa45'])
def sprint45air(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['snj'])
def sneakjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    jump(player, args)

@command(aliases=['wj'])
def walkjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    jump(player, args)

@command(aliases=['lwj'])
def lwalkjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))

    def update():
        args['strafe'] = fl(0)

    jump(player, args, after_jump_tick = update)

@command(aliases=['rwj'])
def rwalkjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(-1))

    def update():
        args['strafe'] = fl(0)

    jump(player, args, after_jump_tick = update)

@command(aliases=['sj'])
def sprintjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    jump(player, args)

@command(aliases=['lsj'])
def lsprintjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))
    args.setdefault('sprinting', True)

    def update():
        args['strafe'] = fl(0)

    jump(player, args, after_jump_tick = update)

@command(aliases=['rsj'])
def rsprintjump(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(-1))
    args.setdefault('sprinting', True)

    def update():
        args['strafe'] = fl(0)

    jump(player, args, after_jump_tick = update)

@command(aliases=['snj45'])
def sneakjump45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sneaking', True)
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    jump(player, args)

@command(aliases=['wj45'])
def walkjump45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))
    args['function_offset'] = fl(45)
    jump(player, args)

@command(aliases=['sj45'])
def sprintjump45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('sprinting', True)
    
    def update():
        args.setdefault('strafe', fl(1))
        args['function_offset'] = fl(45)
    
    jump(player, args, after_jump_tick = update)

@command(aliases=['lsj45'])
def lsprintjump45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('forward', fl(1))
    args.setdefault('strafe', fl(1))
    args.setdefault('sprinting', True)
    
    args['function_offset'] = fl(-45)
    
    jump(player, args)

@command(aliases=['rsj45'])
def rsprintjump45(player, args, duration = 1, rotation: fl = None):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('sprintjumptick', True)
    args.setdefault('direction', args.get('facing', player.default_facing) + 45)
    args.setdefault('facing', args.get('direction') - 45)
    jump(player, args)

@command(aliases=['st'])
def stop(player, args, duration = 1):
    move(player, args)

@command(aliases=['sta'])
def stopair(player, args, duration = 1):
    args.setdefault('airborne', True)
    move(player, args)

@command(aliases=['stj'])
def stopjump(player, args, duration = 1):
    jump(player, args)

@command(name='|')
def reset_position(player, args):
    player.x = 0
    player.z = 0

@command(name='b')
def mm_to_blocks(player, args):
    if player.x > 0:
        player.x += 0.6
    elif player.x < 0:
        player.x -= 0.6

    if player.z > 0:
        player.z += 0.6
    elif player.z < 0:
        player.z -= 0.6

@command(name='mm')
def blocks_to_mm(player, args):
    if player.x > 0:
        player.x -= 0.6
    elif player.x < 0:
        player.x += 0.6

    if player.z > 0:
        player.z -= 0.6
    elif player.z < 0:
        player.z += 0.6

@command(aliases = ['v'])
def setv(player, args, vx = 0.0, vz = 0.0):
    player.vx = vx
    player.vz = vz

@command(aliases = ['vx'])
def setvx(player, args, vx = 0.0):
    player.vx = vx

@command(aliases = ['vz'])
def setvz(player, args, vz = 0.0):
    player.vz = vz

@command(aliases = ['pos', 'xz'])
def setpos(player, args, x = 0.0, z = 0.0):
    player.x = x
    player.z = z

@command(aliases = ['posx', 'x'])
def setposx(player, args, x = 0.0):
    player.x = x

@command(aliases = ['posz', 'z'])
def setposz(player, args, z = 0.0):
    player.z = z

@command(aliases = ['slip'])
def setslip(player, args, slip = fl(0)):
    player.ground_slip = slip

@command(aliases = ['angle', 'a'])
def angles(player, args, angles = -1):
    player.angles = angles

@command()
def inertia(player, args, inertia = 0.005):
    player.inertia_threshold = inertia

@command(aliases = ['pre'])
def precision(player, args, precision = 6):
    player.printprecision = precision

@command(aliases = ['facing', 'face', 'f'])
def rotation(player, args, rotation = 0):
    player.default_rotation = rotation

@command(aliases = ['offrotation', 'offrot', 'orotation', 'orot', 'or',
                    'offsetfacing', 'offfacing', 'offface', 'ofacing', 'oface', 'of'])
def offsetrotation(player, args, rotation = 0):
    player.rotation_offset = rotation

@command(aliases = ['ssand', 'ss'])
def soulsand(player, args, soulsand = 1):
    player.soulsand = soulsand