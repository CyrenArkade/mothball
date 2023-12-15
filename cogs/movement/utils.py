from math import sin
from numpy import float32 as f32

class SimNode():
    def __init__(self, msgid, botmsg, player):
        self.msgid = msgid
        self.botmsg = botmsg
        self.player = player
        self.children = []

class SimError(Exception):
    pass

class Function():
    def __init__(self, name, args, arg_names):
        self.type = type
        self.args = args
        self.arg_names = arg_names


pi = 3.14159265358979323846
fastmath_sin_table = [0] * 4096
for i in range(4096):
    fastmath_sin_table[i] = f32(sin((f32(i) + f32(0.5)) / f32(4096) * (f32(pi) * f32(2))))
for i in range(4):
    fastmath_sin_table[int(f32(i*90) * f32(11.377778)) & 4095] = f32(sin(f32(i*90) * f32(0.017453292)))