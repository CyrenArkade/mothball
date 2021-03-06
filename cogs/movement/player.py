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
        self.facing_offset = 0
        self.inertia_threshold = 0.005
        self.soulsand = 0

        self.history = []
        self.printprecision = 6

    def __str__(self) -> str:
        zstr = str(round(self.z, self.printprecision))
        xstr = str(round(self.x, self.printprecision))
        max_length = max(len(zstr), len(xstr))

        out = f'X = {xstr.ljust(max_length + 5, " ")}Vx = {round(self.vx, self.printprecision)}\n'
        out +=  f'Z = {zstr.ljust(max_length + 5, " ")}Vz = {round(self.vz, self.printprecision)}'
        return out
    
    def log(self):
        self.history.append((self.x, self.z, self.vx, self.vz))
    
    def clearlogs(self):
        self.history = []
    
    def history_string(self):
        history = ''
        for tick in self.history:
            history += (f'x/z:({round(tick[0], self.printprecision)}, {round(tick[1], self.printprecision)})'.ljust(27))
            history += f'vx/vz:({round(tick[2], self.printprecision)}, {round(tick[3], self.printprecision)})\n'
        return '```' + history + '```'

    def softcopy(self):
        other = Player()

        other.x = self.x
        other.z = self.z
        other.vx = self.vx
        other.vz = self.vz
        other.prev_slip = self.prev_slip
        other.ground_slip = self.ground_slip
        other.eff_mult = self.eff_mult
        other.angles = self.angles
        other.default_facing = self.default_facing
        other.facing_offset = self.facing_offset
        other.inertia_threshold = self.inertia_threshold
        other.soulsand = self.soulsand

        return other