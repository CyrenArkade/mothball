from sys import float_info

def height(player, args):
    args.setdefault('duration', 12)
    args.setdefault('ceiling', float_info.max)
    args.setdefault('eff_mult', args.get('jump_boost', 0) * 0.1)

    vy = 0.42 + args.get('eff_mult')
    y = 0

    for i in range(args.get('duration') - 1):
        y = y + vy
        if y > args.get('ceiling') - 1.8:
            y = args.get('ceiling') - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < player.inertia_threshold:
            vy = 0
        print(i + 2, y)
    
    outstring = f' with a {args.get("ceiling")}bc' if args.get('ceiling') != float_info.max else ''
    
    return round(y, 6), f'Height after {args.get("duration")} ticks{outstring}: **{round(y, 6)}**'

def duration(player, args):
    args.setdefault('floor', 0)
    args.setdefault('ceiling', float_info.max)
    args.setdefault('eff_mult', args.get('jump_boost', 0) * 0.1)

    vy = 0.42 + args.get('eff_mult')
    y = 0
    ticks = 0

    while y > args.get('floor') or vy > 0:
        y = y + vy
        if y > args.get('ceiling') - 1.8:
            y = args.get('ceiling') - 1.8
            vy = 0
        vy = (vy - 0.08) * 0.98
        if abs(vy) < player.inertia_threshold:
            vy = 0
        ticks += 1
    
    outstring = f' {args.get("ceiling")}bc' if args.get('ceiling') != float_info.max else ''
    
    return ticks, f'Duration of a {args.get("floor"):+.1f}b{outstring} jump: **{ticks} ticks**'