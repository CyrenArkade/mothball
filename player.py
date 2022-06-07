class Player:
    def __init__(self):
        self.x = 0
        self.z = 0
        self.vx = 0
        self.vz = 0
        self.prev_slip = None
        self.ground_slip = 0.6
        self.eff_mult = 1
        self.angles = -1
        self.default_facing = 0
        self.inertia_threshold = 0.005

        self.history = []

    def __str__(self) -> str:
        zstr = str(round(self.z, 6))
        xstr = str(round(self.x, 6))
        max_length = max(len(zstr), len(xstr))

        out = f'X = {xstr.ljust(max_length + 5, " ")}Vx = {round(self.vx, 6)}\n'
        out +=  f'Z = {zstr.ljust(max_length + 5, " ")}Vz = {round(self.vz, 6)}'
        return out
    
    def log(self):
        self.history.append((self.x, self.z, self.vx, self.vz))
    
    def history_string(self):
        history = ''
        for tick in self.history:
            history += (f'x/z:({round(tick[0], 6)}, {round(tick[1], 6)})'.ljust(27))
            history += f'vx/vz:({round(tick[2], 6)}, {round(tick[3], 6)})\n'
        return '```' + history + '```'