from copy import deepcopy
from numpy import format_float_positional

class Context():
    def __init__(self, player, envs, is_dev):

        self.player = player
        self.envs = envs
        self.is_dev = is_dev

        self.macro = None
        self.out = ''
        self.pre_out = ''
        self.input_history = []
        self.history = []
        self.print_precision = 6
    
    def child(self):
        return Context(deepcopy(self.player), self.envs, self.is_dev)

    def format(self, num, sign = False):
        if num is None:
            return 'None'
        return format_float_positional(num, trim='-', precision=self.print_precision, sign=sign)

    def result(self):

        if not self.out:
            if any([n != 0 for n in (self.player.x, self.player.z, self.player.vx, self.player.vz)]):
                self.out += self.default_string()
            else:
                self.out += '​\U0001f44d'

        return self.pre_out + self.out
    
    def default_string(self):
        xstr = self.format(self.player.x + self.player.modx)
        zstr = self.format(self.player.z + self.player.modz)
        max_length = max(len(xstr), len(zstr))
        out =  f'X = {xstr.ljust(max_length + 5, " ")}Vx = {self.format(self.player.vx)}\n'
        out += f'Z = {zstr.ljust(max_length + 5, " ")}Vz = {self.format(self.player.vz)}\n'
        return out

    def history_string(self):
        history = ''
        for tick in self.history:
            history += (f'x/z:({self.format(tick[0]+self.player.modx)}, {self.format(tick[1]+self.player.modz)})'.ljust(15 + 2 * self.print_precision))
            history += f'vx/vz:({self.format(tick[2])}, {self.format(tick[3])})\n'
        return '```' + history + '```'

    def macro_csv(self):

        # 0: forward
        # 1: strafe
        # 2: sprinting
        # 3: sneaking
        # 4: jumping
        # 5: rotation

        lines = ['X,Y,Z,YAW,PITCH,ANGLE_X,ANGLE_Y,W,A,S,D,SPRINT,SNEAK,JUMP,LMB,RMB,VEL_X,VEL_Y,VEL_Z']

        prev_rotation = None
        for tick in self.input_history:
            w = a = s = d = 'false'
            if tick[0] > 0: w = 'true'
            if tick[0] < 0: s = 'true'
            if tick[1] > 0: a = 'true'
            if tick[1] < 0: d = 'true'
            input_str = f'{w},{a},{s},{d},{str(tick[2]).lower()},{str(tick[3]).lower()},{str(tick[4]).lower()}'

            if prev_rotation is None:
                turn = 0
            else:
                turn = tick[5] - prev_rotation

            prev_rotation = tick[5]
            lines.append(f'0.0,0.0,0.0,0.0,0.0,{turn},0.0,{input_str},false,false, 0.0, 0.0, 0.0')

        return '\n'.join(lines)
