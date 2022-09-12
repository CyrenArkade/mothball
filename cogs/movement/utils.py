from math import sin
from numpy import float32 as fl

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
    fastmath_sin_table[i] = fl(sin((fl(i) + fl(0.5)) / fl(4096) * (fl(pi) * fl(2))))