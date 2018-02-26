# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam, Simulation, Strategy, show_simu, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT
from ia.strategies import FonceurStrategy, FonceurChallenge1Strategy
from ia.tools import StateFoot
from ia.conditions import can_shoot
import random

class dictParams(object):
    def __init__(self):
        self.params = {"alpha": 0., "beta":0., "power":0.,"tempsI":0, "angle";0.}

    @classmethod
    def limits(cls):
        return {"alpha": (0.,0.), "beta":(0.,0.), "power":(0.,0.),"tempsI":(0.,0.), \
                "angle";(0.,0.)}
    
    def random(self, parameters):
        limits = dictParams.limits()
        for p in parameters:
            pLimits = limits[p]
            self.params[p] = random.uniform(pLimits[0], pLimits[1])

    def isValid(self, p):
        val = self.params[p]
        limits = dictParams.limits()
        return val >= limits[p][0] and val <= limits[p][1]
        
class GKStrikerTeam(object):
    def __init__(self, size=10):
        self.team = None
        self.gk = GardienStrategy()
        self.st = FonceurStrategy()
        self.params = [dictParams()]*size
        self.gk_params = ["tempsI"]
        self.st_params = ["alpha", "beta", "angle"]

    def initialize(self):
        for p in self.params:
            p.random(self.gk_params + self.st_params)

    def get_team(self, i):
        params = self.params[i]
        for p in self.gk_params:
            self.gk.dictGK[p] = params[p]
        for p in self.st_params:
            self.st.dictST[p] = params[p]
        self.team = SoccerTeam("GKStriker")
        self.team.add(self.gk.name, self.gk)
        self.team.add(self.st.name, self.st)
        return self.team

    def crossover(self, i, j):
        """
        Proabiblite de faire un crossover ; 0.7
        """
        p1 = self.params[i]
        p2 = self.params[j]
        p1new = p1.deepcopy()
        p2new = p2.deepcopy()
        pList = self.gk_params + self.st_params
        index = random.randrange(0, len(pList))
        for i in range(index):
            p1new.params[pList[i]] = p2.params[pList[i]]
            p2new.params[pList[i]] = p1.params[pList[i]]
        self.params[i] = p1new
        self.params[j] = p2new

    def addNoise(self, i, p):
        val = self.params[i].params[p]
        while True:
            valNoise = val * random.uniform(0.9,1.1)
            if valNois == val: continue
            self.params[i].params[p] = valNoise
            if self.params[i].isValid(p):
                break
    
    def mutation(self, i, j):
        """
        Proabiblite de faire une mutation ; 0.01 - 0.1 (a definir)
        """
        self.crossover(i, j)
        pList = self.gk_params + self.st_params
        pi = random.randrange(0, len(pList))
        self.addNoise(index, i, pList[pi])
        pj = random.randrange(0, len(pList))
        self.addNoise(index, j, pList[pj])
        
    def begin_match(self, team1, team2, state):
        self.last = 0  # Step of the last round
        self.crit = 0  # Criterion to maximize (here, number of goals)
        self.cpt = 0  # Counter for trials
        self.param_keys = list(self.params.keys())  # Name of all parameters
        self.param_id = [0] * len(self.params)  # Index of the parameter values
        self.param_id_id = len(self.params) - 1  # Index of the current parameter
        self.res = dict()  # Dictionary of results

    def begin_round(self, team1, team2, state):
        dist = self.params['dist'][0]
        ball = Vector2D.create_random(low=-1, high=1)
        if ball.x < 0. : ball.x = -ball.x 
        aleat = Vector2D.create_random(low=15, high=dist)
        ball.normalize().scale(aleat.x)
        ball.y += GAME_HEIGHT/2.
    
        # Player and ball postion (random)
        self.simu.state.states[(2, 0)].position = ball.copy()  # Shooter position
        self.simu.state.states[(2, 0)].vitesse = Vector2D()  # Shooter acceleration
        self.simu.state.ball.position = ball.copy()  # Ball position

        # Last step of the game
        self.last = self.simu.step

        # Set the current value for the current parameter
        for i, (key, values) in zip(self.param_id, self.params.items()):
            setattr(self.strategy, key, values[i])

    def update_round(self, team1, team2, state):
        # Stop the round if it is too long
        if state.step > self.last + self.max_round_step:
            self.simu.end_round()

    def end_round(self, team1, team2, state):
        # A round ends when there is a goal
        if state.goal > 0:
            self.crit += 1  # Increment criterion

        self.cpt += 1  # Increment number of trials
        if self.cpt >= self.trials:
            # Save the result
            res_key = tuple()
            for i, values in zip(self.param_id, self.params.values()):
                res_key += values[i],
            self.res[res_key] = self.crit * 1. / self.trials
            print(res_key, self.crit)

            # Reset parameters
            self.crit = 0
            self.cpt = 0

            # Go to the next parameter value to try
            key3 = self.param_keys[self.param_id_id]
            key2 = self.param_keys[self.param_id_id-1]
            key1 = self.param_keys[self.param_id_id-2]
            if self.param_id[self.param_id_id] < len(self.params[key3]) - 1:
                self.param_id[self.param_id_id] += 1
            elif self.param_id[self.param_id_id-1] < len(self.params[key2]) - 1:
                self.param_id[self.param_id_id] = 0
                self.param_id[self.param_id_id-1] += 1
            elif self.param_id[self.param_id_id-2] < len(self.params[key1]) - 1:
                self.param_id[self.param_id_id] = 0
                self.param_id[self.param_id_id-1] = 0
                self.param_id[self.param_id_id-2] += 1
                self.param_id_id += 1
            else:
                self.simu.end_match()

        for i, (key, values) in zip(self.param_id, self.params.items()):
            print("{}: {}".format(key, values[i]), end="   ")
        print("Crit: {}   Cpt: {}".format(self.crit, self.cpt))

    def get_res(self):
        return self.res
