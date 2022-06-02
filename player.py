class Player:
    x = 0
    z = 0
    vx = 0
    vz = 0
    prev_slip = None
    ground_slip = 0.6
    eff_mult = 1
    default_facing = 0
    inertia_threshold = 0.005

    def __str__(self) -> str:
        zstr = str(round(self.z, 6))
        xstr = str(round(self.x, 6))
        max_length = max(len(zstr), len(xstr))

        out =  f'Z = {zstr.ljust(max_length + 5)}Vz = {round(self.vz, 6)}\n'
        out += f'X = {xstr.ljust(max_length + 5)}Vx = {round(self.vx, 6)}'
        return out