import math
from commandmanager import player_command

# Valid arguments: direction, facing, slip, airborne, mov_mult, eff_mult, sprintjumptick
def move(player, args):
    if args.get('airborne'):
        slip = 1
    else:
        slip = args.get('slip', player.ground_slip)
    
    if player.prev_slip is None:
        player.prev_slip = slip
    
    airborne = args.get('airborne', False)
    facing = args.get('facing', player.default_facing)
    direction = args.get('direction', facing)
    mov_mult = args.get('mov_mult', 1)
    eff_mult = args.get('eff_mult', player.eff_mult)
    sprintjumptick = args.get('sprintjumptick', False)

    if args.get('duration', 0) < 0:
        facing += 180
        direction += 180
    
    # Moves the player
    player.x += player.vx
    player.z += player.vz

    # Inertia threshold
    if abs(player.vx * slip * 0.91) < player.inertia_threshold:
        player.vx = 0
    if abs(player.vz * slip * 0.91) < player.inertia_threshold:
        player.vz = 0
    
    # Updates momentum
    player.vx = player.vx * player.prev_slip * 0.91
    player.vz = player.vz * player.prev_slip * 0.91

    # Applies acceleration
    if airborne:
        player.vx += 0.02 * mov_mult * math.sin(math.radians(direction))
        player.vz += 0.02 * mov_mult * math.cos(math.radians(direction))
    else:
        player.vx += 0.1 * mov_mult * eff_mult * (0.6 / slip) ** 3 * math.sin(math.radians(direction))
        player.vz += 0.1 * mov_mult * eff_mult * (0.6 / slip) ** 3 * math.cos(math.radians(direction))
        if sprintjumptick:
            player.vx += 0.2 * math.sin(math.radians(facing))
            player.vz += 0.2 * math.cos(math.radians(facing))

    player.prev_slip = slip


def basic_move(player, args):
    args.setdefault('duration', 1)
    for i in range(abs(args['duration'])):
        move(player, args)

def jump(player, args, apply=lambda:None):
    args.setdefault('duration', 1)
    move(player, args)

    args.setdefault('airborne', True) 
    args.pop('sprintjumptick', None)

    apply()
    
    for i in range(abs(args['duration']) - 1):
        move(player, args)

@player_command(aliases=['w'], arguments=['duration', 'facing'])
def walk(player, args):
    args.setdefault('mov_mult', 0.98)
    basic_move(player, args)

@player_command(aliases=['s'], arguments=['duration', 'facing'])
def sprint(player, args):
    args.setdefault('mov_mult', 1.274)
    basic_move(player, args)

@player_command(aliases=['sn'], arguments=['duration', 'facing'])
def sneak(player, args):
    args.setdefault('mov_mult', 0.294)
    basic_move(player, args)

@player_command(aliases=['w45'], arguments=['duration', 'facing'])
def walk45(player, args):
    args.setdefault('mov_mult', 1)
    basic_move(player, args)

@player_command(aliases=['s45'], arguments=['duration', 'facing'])
def sprint45(player, args):
    args.setdefault('mov_mult', 1.3)
    basic_move(player, args)

@player_command(aliases=['sn45'], arguments=['duration', 'facing'])
def sneak45(player, args):
    args.setdefault('mov_mult', 0.294 * math.sqrt(2))
    basic_move(player, args)

@player_command(aliases=['sna'], arguments=['duration', 'facing'])
def sneakair(player, args):
    args.setdefault('mov_mult', 0.294)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['wa'], arguments=['duration', 'facing'])
def walkair(player, args):
    args.setdefault('mov_mult', 0.98)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['sa'], arguments=['duration', 'facing'])
def sprintair(player, args):
    args.setdefault('mov_mult', 1.274)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['sn45a'], arguments=['duration', 'facing'])
def sneak45air(player, args):
    args.setdefault('mov_mult', 0.294 * math.sqrt(2))
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['w45a'], arguments=['duration', 'facing'])
def walk45air(player, args):
    args.setdefault('mov_mult', 1)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['s45a'], arguments=['duration', 'facing'])
def sprint45air(player, args):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(aliases=['snj'], arguments=['duration', 'facing'])
def sneakjump(player, args):
    args.setdefault('mov_mult', 0.3)
    jump(player, args)

@player_command(aliases=['wj'], arguments=['duration', 'facing'])
def walkjump(player, args):
    args.setdefault('mov_mult', 0.98)
    jump(player, args)

@player_command(aliases=['sj'], arguments=['duration', 'facing'])
def sprintjump(player, args):
    args.setdefault('mov_mult', 1.274)
    args.setdefault('sprintjumptick', True)
    jump(player, args)

@player_command(aliases=['lsj'], arguments=['duration', 'facing'])
def lsprintjump(player, args):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('sprintjumptick', True)
    args.update({'direction': args.get('facing', player.default_facing) - 45})
    def update():
        args.pop('direction')
        args.update({'mov_mult': args.get('mov_mult') * 0.98})
    jump(player, args, apply = update)

@player_command(aliases=['rsj'], arguments=['duration', 'facing'])
def rsprintjump(player, args):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('sprintjumptick', True)
    args.update({'direction': args.get('facing', player.default_facing) + 45})
    def update():
        args.pop('direction')
        args.update({'mov_mult': args.get('mov_mult') * 0.98})
    jump(player, args, apply = update)

@player_command(aliases=['wj45'], arguments=['duration', 'facing'])
def walkjump45(player, args):
    args.setdefault('mov_mult', 1)
    jump(player, args)

@player_command(aliases=['sj45'], arguments=['duration', 'facing'])
def sprintjump45(player, args):
    args.setdefault('mov_mult', 1.274)
    args.setdefault('sprintjumptick', True)
    update = lambda: args.update({'mov_mult': args.get('mov_mult') / 0.98})
    jump(player, args, apply = update)

@player_command(aliases=['lsj45'], arguments=['duration', 'direction'])
def lsprintjump45(player, args):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('sprintjumptick', True)
    args.setdefault('direction', args.get('facing', player.default_facing) - 45)
    args.setdefault('facing', args.get('direction') + 45)
    jump(player, args)

@player_command(aliases=['rsj45'], arguments=['duration', 'direction'])
def rsprintjump45(player, args):
    args.setdefault('mov_mult', 1.3)
    args.setdefault('sprintjumptick', True)
    args.setdefault('direction', args.get('facing', player.default_facing) + 45)
    args.setdefault('facing', args.get('direction') - 45)
    jump(player, args)

@player_command(aliases=['snj45'], arguments=['duration', 'facing'])
def sneakjump45(player, args):
    args.setdefault('mov_mult', 0.294 * math.sqrt(2))
    jump(player, args)

@player_command(aliases=['st'], arguments=['duration'])
def stop(player, args):
    args.setdefault('mov_mult', 0)
    basic_move(player, args)

@player_command(aliases=['sta'], arguments=['duration'])
def stopair(player, args):
    args.setdefault('mov_mult', 0)
    args.setdefault('airborne', True)
    basic_move(player, args)

@player_command(name='|')
def reset_position(player, args):
    player.x = 0
    player.z = 0

@player_command(name='b')
def mm_to_blocks(player, args):
    player.x += 0.6
    player.z += 0.6

@player_command(name='mm')
def blocks_to_mm(player, args):
    player.x -= 0.6
    player.z -= 0.6

@player_command(aliases = ['v'], arguments=['vx', 'vz'])
def setv(player, args):
    player.vx = args.get('vx', 0)
    player.vz = args.get('vz', 0)

@player_command(aliases = ['vx'], arguments=['vx'])
def setvx(player, args):
    player.vx = args.get('vx', 0)

@player_command(aliases = ['vz'], arguments=['vz'])
def setvz(player, args):
    player.vz = args.get('vz', 0)

@player_command(aliases = ['slip'], arguments=['slip'])
def setslip(player, args):
    args.setdefault('slip', 0.6)
    player.ground_slip = args['slip']

@player_command(aliases = ['eff'], arguments=['eff_mult'])
def seteff(player, args):
    args.setdefault('eff_mult', 1)
    player.eff_mult = args['eff_mult']
