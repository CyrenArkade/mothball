# Mothball
A Discord bot for simulating Minecraft movement.

## Commands
`;[simulate | sim | s]`​`functions` Simulates the provided functions and displays the final result.

`;[history | h]`​`functions` Simulates the provided functions and displays tick by tick results.

`;[then | t]`​`functions` Continues simulation from the reply and displays the final result.

`;[thenh | th]`​`functions` Continues simulation from the reply and displays tick by tick results.

## Function Syntax
Functions must be separated by spaces. They consist of the function name, optionally followed by arguments in parenthesis. Args must be separated by commas.

### Functions
Movement names are generally of the format `[stop, sneak, walk, sprint]`​`[air, jump]`​`[45]`. Only the first component is required.
These can be shortened down to `[st, sn, w, s]`​`[a, j]`​`[45]`.

Exceptions include the strafe sprintjump variants, which are prefixed with `[l, r]`.

A table of more exotic functions:

| Function     | Alias(es) | Arguments                 | Result                                                                                           |
|--------------|-----------|---------------------------|--------------------------------------------------------------------------------------------------|
| \|           |           |                           | Resets the player's position                                                                     |
| b            |           |                           | Adds 0.6 to the player's x/z positions                                                           |
| mm           |           |                           | Subtracts 0.6 from the player's x/z positions                                                    |
| setv         | v         | vx, vz                    | Sets the player's x and z velocities                                                             |
| setvx        | vx        | vx                        | Sets the player's x velocity                                                                     |
| setvz        | vz        | vz                        | Sets the player's z velocity                                                                     |
| setpos       | pos       | x, z                      | Sets the player's x and z positions                                                              |
| setposx      | posx, x   | x                         | Sets the player's x position                                                                     |
| setposz      | posz, z   | z                         | Sets the player's z position                                                                     |
| setslip      | slip      | slip                      | Sets the player's default ground slipperiness                                                    |
| seteff       | eff       | eff_mult, speed, slowness | Sets the player's default effect multiplier. Will calculate effmult if speed/slowness are given. |
| angles       | angle     | angles                    | Sets the player's default number of significant angles                                           |
| precision    | pre       | precision                 | Sets the number of decimals in the output                                                        |
| inertia      |           | inertia                   | Sets the player's inertia threshold                                                              |
| facing       | face, f   | facing                    | Sets the player's default facing                                                                 |
| offsetfacing | oface, of | facing                    | Offsets the player's facing                                                                      |

### Arguments
Positional arguments are defined by their positions to one another. Keyworded arguments are given by `argument`​`=`​`value`.

Most movement functions have the positonal args `duration, direction`, which default to 1 and the player's default facing, respectively. Many functions include default values for arguments like mov_mult that can be overriden to provide custom behavior.

| Argument       | Alias(es)       | Effect                                                                                                  |
|----------------|-----------------|---------------------------------------------------------------------------------------------------------|
| duration       | dur, t          | Determines the duration of the action                                                                   |
| direction      | dir, d          | Determines the direction of player movement                                                             |
| facing         | face, f         | Determines the direction the player faces                                                               |
| slip           | s               | Determines the slipperiness of the ground                                                               |
| airborne       | air             | Determines if the player is considered midair                                                           |
| mov_mult       | movmult, mov, m | Determines the player's movement multiplier                                                             |
| eff_mult       | effmult, eff, e | Determines the player's effect multiplier                                                               |
| speed          | spd             | Determines the player's speed level. Overrides eff_mult.                                                |
| slowness       | slow            | Determines the player's slowness level. Overrides eff_mult.                                             |
| angles         | angle           | Determines the number of significant angles trigonometry functions assume. Defaults to -1, or infinite. |
| sprintjumptick | sprintjump      | Determines if the player is sprintjumping                                                               |

Adding arguments to functions clearly not designed for them will produce unpredictable and impossible results.

### The repeat function
The repeat function lets you repeat a function or a series of functions multiple times. An example: `repeat(sprintjump(12), 2)`
