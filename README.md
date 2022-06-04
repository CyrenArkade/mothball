# Mothball
A Discord bot for simulating Minecraft movement.

## Function Syntax
Functions must be separated by spaces. They consist of the function name, optionally followed by arguments in parenthesis. Args must be separated by commas.

### Functions
Movement names are generally of the format `[sneak, walk, sprint]`​`[air, jump]`​`[45]`. Only the first component is required.
These can be shortened down to `[sn, w, s]`​`[a, j]`​`[45]`.

Exceptions include the strafe sprintjump variants, which are prefixed with `[l, r]`.

A table of more exotic functions:

| Function | Alias(es) | Arguments | Result                                        |
|----------|-----------|-----------|-----------------------------------------------|
| \|       |           |           | Resets the player's position                  |
| b        |           |           | Adds 0.6 to the player's x/z positions        |
| mm       |           |           | Subtracts 0.6 from the player's x/z positions |
| setv     | v         | vx, vz    | Sets the player's x and z velocities          |
| setvx    | vx        | vx        | Sets the player's x velocity                  |
| setvy    | vz        | vz        | Sets the player's z velocity                  |
| setslip  | slip      | slip      | Sets the player's default ground slipperiness |
| seteff   | eff       | eff_mult  | Sets the player's default effect multiplier   |

### Arguments
Positional arguments are defined by their positions to one another. Keyworded arguments are given by `argument`​`=`​`value`.

Most movement functions have the positonal args `duration, direction`, which default to 1 and the player's default facing, respectively. Many functions include default values for arguments like mov_mult that can be overriden to provide custom behavior.

| Argument       | Alias(es)       | Effect                                        |
|----------------|-----------------|-----------------------------------------------|
| duration       | dur, t          | Determines the duration of the action         |
| direction      | dir, d          | Determines the direction of player movement   |
| facing         | face, f         | Determines the direction the player faces     |
| slip           | s               | Determines the slipperiness of the ground     |
| airborne       | air             | Determines if the player is considered midair |
| mov_mult       | movmult, mov, m | Determines the player's movement multiplier   |
| eff_mult       | effmult, eff, e | Determines the player's effect multiplier     |
| sprintjumptick | sprintjump      | Determines if the player is sprintjumping     |

### The repeat function
The repeat function lets you repeat a function or a series of functions multiple times. An example: `repeat(sprintjump(12), 2)`
