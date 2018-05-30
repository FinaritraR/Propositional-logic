

import numpy as np
import timeit
from queue import *
from math import *
from logic import *

import sys
sys.setrecursionlimit(10000)

class WumpusWorld:
    def __init__(self, world_config):

        #agent starts at 1,1 and face East
        #North = 0, East = 90, South = 180 and West = 270
        # The order of sensations are: breeze, stench, glitter, bump, scream
        self.config = world_config
        self.position = [1, 1]
        self.facing = 90
        self.percepts = []

        #The propositional knowledge base
        # payoff of the agent
        self.kbase = generate_prop_kb(len(self.config))
        self.grid = int(sqrt(len(self.config)))
        self.payoff = 0
        self.time_step = 0
        self.terminated = False

        #action sequence of the agent
        self.actions = []

    def terminated(self):
        return self.terminated

    def percept(self):

       #Percept the room
        self.percepts.clear()

        position_str = str(self.position[0]) + str(self.position[1])
        agent_position_arr = self.grid * (self.grid - self.position[1]) + self.position[0] - 1

        # Die if same room as wumpus or pit
        if 'W' in self.config[agent_position_arr]:
            self.percepts.append('Wumpus')
            return
        elif 'P' in self.config[agent_position_arr]:
            self.percepts.append('Pit')
            return
        elif 'G' in self.config[agent_position_arr]:
            self.percepts.append('Glitter')
            return

        self.percepts.append('~W' + position_str)
        self.percepts.append('~P' + position_str)
        self.percepts.append('~G' + position_str)

        stench = 'S' + position_str if 'S' in self.config[agent_position_arr] else '~S' + position_str
        self.percepts.append(stench)
        breeze = 'B' + position_str if 'B' in self.config[agent_position_arr] else '~B' + position_str
        self.percepts.append(breeze)
        bump = 'Bump' if 'Bp' in self.config[agent_position_arr] else '~Bump'
        self.percepts.append(bump)
        scream = 'Scream' if 'Sc' in self.config[agent_position_arr] else '~Scream'
        self.percepts.append(scream)

        # Remove Bump
        if 'Bp' in self.config[agent_position_arr]:
            self.config[agent_position_arr].remove('Bp')

        # Remove Scream
        if 'Sc' in self.config[agent_position_arr]:
            # Remove 'Scream' in list
            self.config[agent_position_arr].remove('Sc')


    def execute_action(self, action):

        if action in ('Die', 'Grab'):
            self.terminated = True
        elif action == 'Forward':
            # Try to move forward (may hit a wall, or get killed by a wumpus or pit)
            self._move_forward()
            self.kbase.tell(expr(make_action_sentence('~Shoot', self.time_step)))

        elif action == 'TurnRight':
            self.facing += 90
            self.kbase.tell(expr(make_action_sentence('~Shoot', self.time_step)))

        elif action == 'TurnLeft':
            self.facing -= 90
            self.kbase.tell(expr(make_action_sentence('~Shoot', self.time_step)))

        else:
            self.shoot_wumpus()

        # Tell kb which action it took
        self.kbase.tell(expr(make_action_sentence(action, self.time_step)))
        # Update payoff and action history
        self.payoff += get_payoff(action)
        self.actions.append(action)
        # Increment time step
        self.time_step += 1

        if self.facing == 0:
            facing = 'North'
        elif self.facing == 90:
            facing = 'East'
        elif self.facing == 180:
            facing = 'South'
        else:
            facing = 'West'
        print('Action taken: ', action, '|| location of agent: ', self.position, ', direction of agent: ', facing)
        print('Payoff at current state: ', self.payoff)


    def dumb_agent(self):
        #actions of the agent based on priority: Grab gold > Shoot > Randomly trying to move forward, turn left or right
        #perform percept
        self.percept()
        for i in self.percepts:

            if i in ('Wumpus', 'Pit'):
                self.execute_action('Die')
                return
            #grab gold when in the room
            elif i == 'Glitter':
                self.execute_action('Grab')
                return
            else:
                self.kbase.tell(expr(make_percept_sentence(i, self.time_step)))

        # Update KB
        self._add_temporal_sentences()

        # If sense stench + arrow: shoot
        if ask(kb=self.kbase, s='HaveArrow', t=self.time_step) and ask(kb=self.kbase, s='S', pos=self.position):
            self.execute_action('Shoot')

        # randomly choose Forward, turn left or turn right
        else:
            move = random.random()
            if move < 0.5:
                self.execute_action('Forward')
            elif 0.5 <= move < 0.75:
                self.execute_action('TurnLeft')
            else:
                self.execute_action('TurnRight')

    def show_result(self):
        print('______________________________________')
        print('_______________ RESULT _______________')
        print('Actions taken:', self.actions)
        print('Payoffs:', self.payoff)

    def _move_forward(self):

        position_arr = self.grid * (self.grid - self.position[1]) + self.position[0] - 1
        if self.facing == 0:  # north
            if self.position[1] == self.grid:
                self.config[position_arr].append('Bp')
            else:
                self.position[1] += 1
        if self.facing == 90:
            if self.position[0] == self.grid:
                self.config[position_arr].append('Bp')
            else:
                self.position[0] += 1
        if self.facing == 180:
            if self.position[1] == 1:
                self.config[position_arr].append('Bp')
            else:
                self.position[1] -= 1
        if self.facing == 270:
            if self.position[0] == 1:
                self.config[position_arr].append('Bp')
            else:
                self.position[0] -= 1

    def _add_temporal_sentences(self):

        # alive and have arrow
        if self.time_step == 0:
            self.kbase.tell(expr('HaveArrowT0 & OK11T0'))

        kb_position = str(self.position[0]) + str(self.position[1])
        kb_time_step = str(self.time_step)
        next_time_step =  str(self.time_step + 1)

        #HaveArrow(t+1) <=> HaveArrow(t) & ~Shoot(t)
        sentence = 'HaveArrowT' + next_time_step + '<=> ( HaveArrowT' + kb_time_step + ' & ~ShootT' + kb_time_step + ')'
        self.kbase.tell(expr(sentence))

        # Ok: OK[x,y](t) <=> ~P[x,y] & ~ W[x,y]
        sentence = 'OK' + kb_position + 'T' + kb_time_step + '<=> (~P' + kb_position + ' & ~W' + kb_position + ')'
        self.kbase.tell(expr(sentence))


    def shoot_wumpus(self):

        wumpus_position = 0
        for i in range(int(pow(self.grid, 2))):
            if 'W' in self.config[i]:
                wumpus_position = i
                break

        agent_pos_arr = self.grid * (self.grid - self.position[1]) + self.position[0] - 1
        # if agent is facing wumpus on the same line then shoot
        if (wumpus_position % self.grid) == (agent_pos_arr % self.grid):
            if (self.facing == 0 and wumpus_position < agent_pos_arr) or (
                            self.facing == 180 and wumpus_position > agent_pos_arr):
                self._wumpus_die(wumpus_position)

        elif (wumpus_position // self.grid) == (agent_pos_arr // self.grid):
            if (self.facing == 90 and wumpus_position > agent_pos_arr) or (
                            self.facing == 270 and wumpus_position < agent_pos_arr):
                self._wumpus_die(wumpus_position)

    def _wumpus_die(self, pos):

        # x,y coordinates of wumpus
        x = pos % self.grid + 1
        y = self.grid - (pos // self.grid)

        self.config[pos].remove('W')

        if pos % self.grid != (self.grid - 1):
            self.config[pos + 1].remove('S')
            self.kbase.retract(expr('S' + str(x + 1) + str(y)))
        if pos % self.grid != 0:
            self.config[pos - 1].remove('S')
            self.kbase.retract(expr('S' + str(x - 1) + str(y)))
        if pos >= self.grid:
            self.config[pos - self.grid].remove('S')
            self.kbase.retract(expr('S' + str(x) + str(y + 1)))
        if pos < int(pow(self.grid, 2)) - self.grid:
            self.config[pos + self.grid].remove('S')
            self.kbase.retract(expr('S' + str(x) + str(y - 1)))

        #add scream
        agent_pos_in_array = self.grid * (self.grid - self.position[1]) + self.position[0] - 1
        self.config[agent_pos_in_array].append('Sc')


def make_action_sentence(action, t):
    return action + 'T' + str(t)

def make_percept_sentence(percept, t):
    if ('Bump' in percept) or ('Scream' in percept):
        return percept + 'T' + str(t)
    else:
        return percept

def get_payoff(action):

    if action == 'Grab':
        return 1000
    elif action == 'Die':
        return -1000
    elif action == 'Shoot':
        return -10
    else:
        return -1

def generate_wumpus_world(size):
    wumpus_world = []
    for i in range(size):
        wumpus_world.append([])

    grid = int(sqrt(size))
    agent_pos = size - grid # [1, 1]

    #room for the wumpus
    wumpus_pos = random.randint(0, size - 1)
    while wumpus_pos == agent_pos:
        wumpus_pos = random.randint(0, size - 1)
    wumpus_world[wumpus_pos].append('W')

    # fill other rooms with stench
    if wumpus_pos < (size - grid):
        wumpus_world[wumpus_pos + grid].append('S')
    if wumpus_pos % grid != (grid - 1):
        wumpus_world[wumpus_pos + 1].append('S')
    if wumpus_pos % grid != 0:
        wumpus_world[wumpus_pos - 1].append('S')
    if wumpus_pos >= grid:
        wumpus_world[wumpus_pos - grid].append('S')

    #room for the gold and glitter
    gold_pos = random.randint(0, size - 1)
    while gold_pos in (wumpus_pos, agent_pos):
        gold_pos = random.randint(0, size - 1)
    wumpus_world[gold_pos].append('G')

    # pits with probability 0.2 for each room
    for i in range(len(wumpus_world)):
        if i not in (gold_pos, agent_pos):
            if random.random() < 0.2:
                wumpus_world[i].append('P')
                #add breeze
                if i % grid != (grid - 1) and 'B' not in wumpus_world[i + 1]:
                    wumpus_world[i + 1].append('B')
                if i % grid != 0 and 'B' not in wumpus_world[i - 1]:
                    wumpus_world[i - 1].append('B')
                if i < size - grid and 'B' not in wumpus_world[i + grid]:
                    wumpus_world[i + grid].append('B')
                if i >= grid and 'B' not in wumpus_world[i - grid]:
                        wumpus_world[i - grid].append('B')

    return wumpus_world


def generate_prop_kb(size):
    k_base = PropKB()
    at_least_one_wumpus = ''
    k_base.tell(expr('~W11'))  # No wumpus in [1,1]
    k_base.tell(expr('~P11'))  # No pit in [1,1]

    grid = int(sqrt(size))



    for k in range(1, 1 + grid):
        position_x, position_lx, position_rx = str(k), str(k - 1), str(k + 1)
        for j in range(1, 1 + grid):
            position_y, position_dy, position_uy = str(j), str(j - 1), str(j + 1)

            pos = position_x + position_y
            up_pos = position_x + position_uy
            down_pos = position_x + position_dy
            left_pos = position_lx + position_y
            right_pos = position_rx + position_y

            # If there's a pit in the room, then all adjacent rooms will have breeze
            # If there's a Wumpus in the room, then all adjacent rooms will have stench
            k_base.tell(
                expr('S' + pos + ' <=> ( W' + left_pos + '| W' + up_pos + '| W' + down_pos + '| W' + right_pos + ')')
            )

            k_base.tell(
                expr('B' + pos + ' <=> ( P' + left_pos + '| P' + up_pos + '| P' + down_pos + '| P' + right_pos + ')')
            )

            # Construct the sentence for there's at least one wumpus in the world
            if not (k == 1 and j == 1):
                at_least_one_wumpus += ' | '
            at_least_one_wumpus += ('W' + pos)


    for k in range(size):
        posx, posy = grid - (k // grid), (k % grid) + 1
        string = '~W' + str(posx) + str(posy)
        for j in range(k + 1, size):
            posxj, posyj = grid - (j // grid), (j % grid) + 1
            jstr = ' | ~W' + str(posxj) + str(posyj)
            k_base.tell(expr(string + jstr))

    # Add the sentence 'at least one wumpus' to kb
    k_base.tell(expr(at_least_one_wumpus))
    return k_base


def ask(kb, s, t=None, pos=None):

    position_str = '' if pos is None else str(pos[0]) + str(pos[1])
    time_str = '' if t is None else 'T' + str(t)
    clauses = ''
    for c in kb.clauses:
        clauses += str(c) + ' & '
    clauses += ('~' + s + position_str + time_str)
    # if we do not find a model that is  unsatisfiable then true
    # DPLL search
    model = dpll_satisfiable(expr(clauses))
    return False if model else True

#run the simulation
def main():
    initial_world = (('S',), (             ), ('B',), ('P',),
                         ('W',), ('B', 'S', 'G'), ('P',), ('B',),
                         ('S',), (             ), ('B',), (    ),
                         (    ), ('B',), ('P',), ('B',))

    # simulation 0 from assignment
    # wumpus_world = WumpusWorldState(initial_world)

    #random simulation
    wumpus_world = WumpusWorld(generate_wumpus_world(16))
    print('World configuration')
    print(wumpus_world.config)

    while not wumpus_world.terminated:
        wumpus_world.dumb_agent()

    wumpus_world.show_result()

if __name__ == '__main__':
    main()



