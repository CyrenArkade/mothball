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