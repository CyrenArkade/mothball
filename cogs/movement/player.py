from numpy import float32 as fl
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
    
    def move(self, ctx):
        args = ctx.args

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
        
        ctx.history.append((self.x, self.z, self.vx, self.vz))
        ctx.input_history.append([forward, strafe, sprinting, sneaking, jumping, rotation])

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
