import random
from logic import *

"""
Generates a wumpus world for the test
Agent: start at [1,1] which is at array index 12
Wumpus: 1 wumpus anywhere except [1,1]
Gold: 1 gold anywhere except the location of wumpus
Pit: Each room with probability 0.2; can be anywhere except the location of agent and gold
:return: Wumpus world configuration in tuple form
"""


def generate_wumpus_world():
    wumpus_world = [[], [], [], [],
                    [], [], [], [],
                    [], [], [], [],
                    [], [], [], []]

    index = random.randint(0, 15)
    while index == 12:
        index = random.randint(0, 15)
    wumpus_world[index].append('W')

    if index % 4 != 0:
        wumpus_world[index - 1].append('S')
    if index > 3:
        wumpus_world[index - 4].append('S')
    if index % 4 != 3:
        wumpus_world[index + 1].append('S')
    if index < 12:
        wumpus_world[index + 4].append('S')

    # gold
    gold_index = random.randint(0, 15)
    while gold_index in (index, 12):
        gold_index = random.randint(0, 15)

    wumpus_world[gold_index].append('G')

    # Generate pits with probability 0.2 for each room
    for i in range(len(wumpus_world)):
        if i not in (gold_index, 12):
            if random.random() < 0.2:
                wumpus_world[i].append('P')
                # Determine sensation 'breeze' in adjacent rooms
                if i % 4 != 0 and 'B' not in wumpus_world[i - 1]:
                    wumpus_world[i - 1].append('B')
                if i > 3 and 'B' not in wumpus_world[i - 4]:
                    wumpus_world[i - 4].append('B')
                if i % 4 != 3 and 'B' not in wumpus_world[i + 1]:
                    wumpus_world[i + 1].append('B')
                if i < 12 and 'B' not in wumpus_world[i + 4]:
                    wumpus_world[i + 4].append('B')

    for i in range(len(wumpus_world)):
        wumpus_world[i] = tuple(wumpus_world[i])
    wumpus_world = tuple(wumpus_world)

    return wumpus_world


def percept(config, pos):
    # grab percepts in the room.

    x = 4;
    percepts = []
    agent_pos_in_array = x * (x - pos[1]) + pos[0] - 1

    stench = 'Stench' \
        if 'S' in config[agent_pos_in_array] else '~Stench'
    percepts.append(stench)

    breeze = 'Breeze' \
        if 'B' in config[agent_pos_in_array] else '~Breeze'
    percepts.append(breeze)

    glitter = 'Glitter' \
        if 'G' in config[agent_pos_in_array] else '~Glitter'
    percepts.append(glitter)

    bump = 'Bump' \
        if 'Bp' in config[agent_pos_in_array] else '~Bump'
    percepts.append(bump)

    scream = 'Scream' \
        if 'Sc' in config[agent_pos_in_array] else '~Scream'
    percepts.append(scream)

    return percepts


world = generate_wumpus_world()
y = percept(world, [1, 1])
print(world)
print(y)
print('il' in 'inline')

elements = set([])
elements.add('this')
elements.add('that')
elements.add('auisdias')
elements.add('what the')
elements.add('that')
elements.add('old')
elements.add('what the')
const = 100
const += 50
wumpus_pos = 0
for i in range(16):
    if 'W' in world[i]:
        wumpus_pos = i
        break
elist = list(elements)
elist.remove('haha') if 'haha' in elist else None
print(elist)

probkb = PropKB()

probkb.tell(expr('P44 & S31'))

probkb.retract(expr('asda'))
print(probkb.clauses)