class SimNode():
    def __init__(self, msgid, botmsg, player):
        self.msgid = msgid
        self.botmsg = botmsg
        self.player = player
        self.children = []