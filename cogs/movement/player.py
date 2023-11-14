from numpy import float32 as fl, format_float_positional
import math
from cogs.movement.utils import fastmath_sin_table

class Player:

    pi = 3.14159265358979323846
    
    def __init__(self):
        self.x = 0.0
        self.z = 0.0
        self.vx = 0.0
        self.vz = 0.0
        self.modx = 0.0
        self.modz = 0.0
        self.prev_slip = None
        self.ground_slip = fl(0.6)
        self.angles = 65536
        self.default_rotation = fl(0.0)
        self.rotation_offset = fl(0.0)
        self.rotation_queue = []
        self.turn_queue = []
        self.prev_sprint = False
        self.air_sprint_delay = True
        self.inertia_threshold = 0.005
        self.soulsand = 0
        self.speed = 0
        self.slowness = 0

        self.macro = None
        self.out = ''
        self.pre_out = ''
        self.input_history = []
        self.prev_rotation = None
        self.history = []
        self.printprecision = 6

    def format(self, num):
        return format_float_positional(num, trim='-', precision=self.printprecision)

    def __str__(self) -> str:

        if self.out == '':
            if any([n != 0 for n in (self.x, self.z, self.vx, self.vz)]):
                self.out += self.default_string()
            else:
                self.out += '​\U0001f44d'

        return self.pre_out + self.out
    
    def clearlogs(self):
        self.history = []
        self.input_history = []
    
    def default_string(self):
        xstr = self.format(self.x + self.modx)
        zstr = self.format(self.z + self.modz)
        max_length = max(len(xstr), len(zstr))
        out =  f'X = {xstr.ljust(max_length + 5, " ")}Vx = {self.format(self.vx)}\n'
        out += f'Z = {zstr.ljust(max_length + 5, " ")}Vz = {self.format(self.vz)}\n'
        return out
    
    def history_string(self):
        history = ''
        for tick in self.history:
            history += (f'x/z:({self.format(tick[0]+self.modx)}, {self.format(tick[1]+self.modz)})'.ljust(15 + 2 * self.printprecision))
            history += f'vx/vz:({self.format(tick[2])}, {self.format(tick[3])})\n'
        return '```' + history + '```'
    
    def macro_csv(self):
        top = 'X,Y,Z,YAW,PITCH,ANGLE_X,ANGLE_Y,W,A,S,D,SPRINT,SNEAK,JUMP,LMB,RMB,VEL_X,VEL_Y,VEL_Z'
        return '\n'.join([top] + self.input_history)

    def softcopy(self):
        other = Player()

        other.x = self.x
        other.z = self.z
        other.vx = self.vx
        other.vz = self.vz
        other.prev_slip = self.prev_slip
        other.ground_slip = self.ground_slip
        other.angles = self.angles
        other.default_rotation = self.default_rotation
        other.rotation_offset = self.rotation_offset
        other.rotation_queue = self.rotation_queue
        other.turn_queue = self.turn_queue
        other.inertia_threshold = self.inertia_threshold
        other.prev_sprint = self.prev_sprint
        other.air_sprint_delay = self.air_sprint_delay
        other.soulsand = self.soulsand
        other.speed = self.speed
        other.slowness = self.slowness

        return other
    
    def move(self, args):

        # Defining variables

        if len(self.rotation_queue) > 0:
            self.default_rotation = self.rotation_queue.pop(0)
        if len(self.turn_queue) > 0:
            self.default_rotation += self.turn_queue.pop(0)

        airborne = args.get('airborne', False)
        rotation = args.get('rotation', self.default_rotation)
        function_offset = args.get('function_offset', fl(0))
        forward = args.get('forward', fl(0))
        strafe = args.get('strafe', fl(0))
        sprinting = args.get('sprinting', False)
        sneaking = args.get('sneaking', False)
        jumping = args.get('jumping', False)
        speed = args.get('speed', self.speed)
        slowness = args.get('slowness', self.slowness)
        soulsand = args.get('soulsand', self.soulsand)
        sprintjump_boost = fl(0.2)

        if airborne:
            slip = fl(1)
        else:
            slip = args.get('slip', self.ground_slip)
        
        self.prev_slip = args.get('prev_slip', self.prev_slip)
        if self.prev_slip is None:
            self.prev_slip = slip
        
        rotation += function_offset + self.rotation_offset

        if args.get('duration', 0) < 0 or 'reverse' in args:
            forward *= fl(-1)
            strafe *= fl(-1)
            sprintjump_boost *= -1
        # End defining
        
        # Moving the player
        self.x += self.vx
        self.z += self.vz

        for _ in range(soulsand):
            self.vx *= 0.4
            self.vz *= 0.4
        
        # Finalizing momentum
        self.vx *= fl(0.91) * self.prev_slip
        self.vz *= fl(0.91) * self.prev_slip

        # Applying inertia threshold
        if abs(self.vx) < self.inertia_threshold:
            self.vx = 0.0
        if abs(self.vz) < self.inertia_threshold:
            self.vz = 0.0

        # Calculating movement multiplier
        inertia = fl(0.91) * slip
        if airborne:
            movement = fl(0.02)
            # Sprinting start/stop is (by default) delayed by a tick midair
            if (self.air_sprint_delay and self.prev_sprint) or (not self.air_sprint_delay and sprinting):
                movement = fl(movement + movement * 0.3)
        else:
            movement = fl(0.1)
            if speed > 0:
                movement = fl(movement * (1.0 + fl(0.2) * float(speed)))
            if slowness > 0:
                movement = fl(movement * max((1.0 + fl(-0.15) * float(slowness)), 0.0))
            if sprinting:
                movement = fl(movement * (1.0 + fl(0.3)))
            movement *= fl(0.16277136) / (inertia * inertia * inertia)
        
        # Applying sprintjump boost
        if sprinting and jumping:
            facing = fl(rotation * fl(0.017453292))
            self.vx -= self.mcsin(facing) * sprintjump_boost
            self.vz += self.mccos(facing) * sprintjump_boost

        # Applies sneaking
        if sneaking:
            forward = fl(float(forward) * 0.3)
            strafe = fl(float(strafe) * 0.3)
        
        forward *= fl(0.98)
        strafe *= fl(0.98)

        distance = fl(strafe * strafe + forward * forward)

        # The if avoids division by zero 
        if distance >= fl(0.0001):

            # Normalizes distance vector only if above 1
            distance = fl(math.sqrt(float(distance)))
            if distance < fl(1.0):
                distance = fl(1.0)

            # Modifies strafe and forward to account for movement
            distance = movement / distance
            strafe = strafe * distance
            forward = forward * distance

            # Adds rotated vectors to velocity
            sin_yaw = fl(self.mcsin(rotation * fl(Player.pi) / fl(180.0)))
            cos_yaw = fl(self.mccos(rotation * fl(Player.pi) / fl(180.0)))
            self.vx += float(strafe * cos_yaw - forward * sin_yaw)
            self.vz += float(forward * cos_yaw + strafe * sin_yaw)

        self.prev_slip = slip
        self.prev_sprint = sprinting
        self.history.append((self.x, self.z, self.vx, self.vz))
        
        w = a = s = d = 'false'
        if forward > 0: w = 'true'
        if forward < 0: s = 'true'
        if strafe > 0: a = 'true'
        if strafe < 0: d = 'true'
        input_str = f'{w},{a},{s},{d},{str(sprinting).lower()},{str(sneaking).lower()},{str(jumping).lower()}'

        if self.prev_rotation is None:
            turn = 0
        else:
            turn = rotation - self.prev_rotation
        self.input_history.append(f'0.0,0.0,0.0,0.0,0.0,{turn},0.0,{input_str},false,false, 0.0, 0.0, 0.0')
        self.prev_rotation = rotation

    def mcsin(self, rad):
        if self.angles == -1:
            return math.sin(rad)
        elif self.angles == 4096:
            index = int(rad * fl(651.8986)) & 4095
            return fastmath_sin_table[index]
        elif self.angles == 65536:
            index = int(rad * fl(10430.378)) & 65535
        else:
            index = int(1 / (2 * Player.pi) * self.angles * rad) & (self.angles - 1)
        return fl(math.sin(index * self.pi * 2.0 / self.angles))

    def mccos(self, rad):
        if self.angles == -1:
            return math.cos(rad)
        elif self.angles == 4096:
            index = int((rad + fl(Player.pi) / fl(2)) * fl(651.8986)) & 4095
            return fastmath_sin_table[index]
        elif self.angles == 65536:
            index = int(rad * fl(10430.378) + fl(16384.0)) & 65535
        else:
            index = int(1 / (2 * Player.pi) * self.angles * rad + self.angles / 4) & (self.angles - 1)
        return fl(math.sin(index * self.pi * 2.0 / self.angles))
