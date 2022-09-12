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
Movement names are generally of the format `[stop, sneak, walk, sprint]`​`[air, jump]`​`[45]`.  
These can be shortened down to `[st, sn, w, s]`​`[a, j]`​`[45]`.

Exceptions include the strafe sprintjump variants, which are prefixed with `[l, r]`.

A table of more exotic functions:

| Function     | Alias(es) | Arguments | Result                                                 |
|--------------|-----------|-----------|--------------------------------------------------------|
| \|           |           |           | Resets the player's position                           |
| b            |           |           | Adds 0.6 to the player's x/z positions                 |
| mm           |           |           | Subtracts 0.6 from the player's x/z positions          |
| setv         | v         | vx, vz    | Sets the player's x and z velocities                   |
| setvx        | vx        | vx        | Sets the player's x velocity                           |
| setvz        | vz        | vz        | Sets the player's z velocity                           |
| setpos       | pos       | x, z      | Sets the player's x and z positions                    |
| setposx      | posx, x   | x         | Sets the player's x position                           |
| setposz      | posz, z   | z         | Sets the player's z position                           |
| setslip      | slip      | slip      | Sets the player's default ground slipperiness          |
| speed        |           | speed     | Sets the player's speed                                |
| slowness     | slow      | slowness  | Sets the player's slowness                             |
| angles       | angle     | angles    | Sets the player's default number of significant angles |
| precision    | pre       | precision | Sets the number of decimals in the output              |
| inertia      |           | inertia   | Sets the player's inertia threshold                    |
| facing       | face, f   | facing    | Sets the player's default facing                       |
| offsetfacing | oface, of | facing    | Offsets the player's facing                            |

### Arguments
Arguments affect only the function in which they are present.

Positional arguments are defined by their positions to one another. Keyworded arguments are given by `argument`​`=`​`value`.

Most movement functions have the positonal args `duration, rotation`, which default to 1 and the player's default rotation, respectively. Many functions include default values for arguments like inertia that can be overriden to provide custom behavior.

| Argument  | Alias(es) | Effect                                     |
|-----------|-----------|--------------------------------------------|
| duration  | dur, t    | Duration of the action                     |
| rotation  | rot, r    | The player's rotation                      |
| slip      | s         | Ground slipperiness                        |
| airborne  | air       | Determines whether the player is airborne  |
| sprinting | sprint    | Determines whether the player is sprinting |
| sneaking  | sneak, sn | Determines whether the player is sneaking  |
| jumping   | jump      | Determines whether the player is jumping   |
| speed     | spd       | Determines the player's speed level.       |
| slowness  | slow      | Determines the player's slowness level.    |

Adding arguments to functions clearly not designed for them will produce unpredictable and impossible results.

### The repeat function
The repeat function lets you repeat a function or a series of functions multiple times. An example: `repeat(sprintjump(12), 2)`

## User-Defined Variables and Functions

Custom variables can be defined with the syntax `var(name, val)`.  
For example, you could define t=12 with `var(t, 12)`, then use the variable with `sprintjump(t)`.

Custom functions can be defined with the syntax `def(name, inputs, *args)`.  
For example, you could define `def(angled_3bc, -wj(duration, angle) -w(1, angle) | sj(duration, angle), duration, angle)`.  
You could then call this function with `angled_3bc(11, 0.0054)`

Functions and variables will persist across channels and servers until Mothball restarts.
