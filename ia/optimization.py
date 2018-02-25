# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam, Simulation, Strategy, show_simu, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT
from ia.strategies import FonceurStrategy
from ia.tools import StateFoot
from ia.conditions import can_shoot

class ParamSearchShoot(object):
    def __init__(self, strategy, params, simu=None, trials=20, max_steps=1000000,
                 max_round_step=40):
        self.strategy = strategy
        self.params = params.copy()
        self.simu = simu
        self.trials = trials
        self.max_steps = max_steps
        self.max_round_step = max_round_step

    def start(self, show=True):
        if not self.simu:
            team1 = SoccerTeam("Team Vide")
            team2 = SoccerTeam("Team Shooter")
            team2.add(self.strategy.name, self.strategy)
            team1.add(Strategy().name, Strategy())
            self.simu = Simulation(team1, team2, max_steps=self.max_steps)
        self.simu.listeners += self

        if show:
            show_simu(self.simu)
        else:
            self.simu.start()

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

class ParamSearchGoal(object):
    def __init__(self, strategy, params, simu=None, trials=20, max_steps=1000000,
                 max_round_step=40):
        self.strategy = strategy
        self.params = params.copy()
        self.simu = simu
        self.trials = trials
        self.max_steps = max_steps
        self.max_round_step = max_round_step

    def start(self, show=True):
        if not self.simu:
            team1 = SoccerTeam("Team Goal")
            team2 = SoccerTeam("Team Shooter")
            team1.add(self.strategy.name, self.strategy)
            team2.add(FonceurStrategy().name, FonceurStrategy())
            self.simu = Simulation(team1, team2, max_steps=self.max_steps)
        self.simu.listeners += self

        if show:
            show_simu(self.simu)
        else:
            self.simu.start()

    def begin_match(self, team1, team2, state):
        self.last = 0  # Step of the last round
        self.crit = 0  # Criterion to maximize (here, number of goals)
        self.cpt = 0  # Counter for trials
        self.param_keys = list(self.params.keys())  # Name of all parameters
        self.param_id = [0] * len(self.params)  # Index of the parameter values
        self.param_id_id = 1  # Index of the current parameter
        self.res = dict()  # Dictionary of results

    def begin_round(self, team1, team2, state):
        ball = Vector2D.create_random(low=-1, high=1)
        if ball.x < 0. : ball.x = -ball.x 
        aleat = Vector2D.create_random(low=15, high=35.)
        ball.normalize().scale(aleat.x)
        ball.y += GAME_HEIGHT/2.
        
        # Player and ball postion (random)
        self.simu.state.states[(2, 0)].position = ball.copy()  # Shooter position
        self.simu.state.states[(2, 0)].vitesse = Vector2D()  # Shooter acceleration
        self.simu.state.states[(1, 0)].position = Vector2D(0., GAME_HEIGHT/2.)  # Goal position
        self.simu.state.states[(1, 0)].vitesse = Vector2D()  # Goal acceleration
        self.simu.state.ball.position = ball.copy()  # Ball position

        # Last step of the game
        self.last = self.simu.step

        # Set the current value for the current parameter
        for i, (key, values) in zip(self.param_id, self.params.items()):
            setattr(self.strategy, key, values[i])
        self.strategy.n_deb = self.params["n"][self.param_id[0]]

    def update_round(self, team1, team2, state):
        me = StateFoot(state, 1 ,0)
        if self.strategy.n <= 0:
            self.simu.end_round()
        
        #if can_shoot(me):
        #    self.crit += 1
        #    self.simu.end_round()
        
        # Stop the round if it is too long
        if state.step > self.last + self.max_round_step:
            self.simu.end_round()

    def end_round(self, team1, team2, state):
        # A round ends when there is a goal
        me = StateFoot(state, 1 ,0)
        if state.goal > 0 or self.strategy.n <= 0:
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
            key2 = self.param_keys[self.param_id_id]
            key1 = self.param_keys[self.param_id_id-1]
            if self.param_id[self.param_id_id] < len(self.params[key2]) - 1:
                self.param_id[self.param_id_id] += 1
            elif self.param_id[self.param_id_id-1] < len(self.params[key1]) - 1:
                self.param_id[self.param_id_id] = 0
                self.param_id[self.param_id_id-1] += 1
            else:
                self.simu.end_match()

        for i, (key, values) in zip(self.param_id, self.params.items()):
            print("{}: {}".format(key, values[i]), end="   ")
        print("Crit: {}   Cpt: {}".format(self.crit, self.cpt))

    def get_res(self):
        return self.res

class ParamSearchDribble(object):
    def __init__(self, strategy, params, simu=None, trials=7, max_steps=1000000,
                 max_round_step=40):
        self.strategy = strategy
        self.params = params.copy()
        self.simu = simu
        self.trials = trials
        self.max_steps = max_steps
        self.max_round_step = max_round_step

    def start(self, show=True):
        if not self.simu:
            team1 = SoccerTeam("Team Dribbler")
            team2 = SoccerTeam("Team Vide")
            team1.add(self.strategy.name, self.strategy)
            team2.add(Strategy().name, Strategy())
            self.simu = Simulation(team1, team2, max_steps=self.max_steps)
        self.simu.listeners += self

        if show:
            show_simu(self.simu)
        else:
            self.simu.start()

    def begin_match(self, team1, team2, state):
        self.last = 0  # Step of the last round
        self.crit = 0  # Criterion to maximize (here, number of goals)
        self.cpt = 0  # Counter for trials
        self.param_keys = list(self.params.keys())  # Name of all parameters
        self.param_id = [0] * len(self.params)  # Index of the parameter values
        self.param_id_id = len(self.params) - 1  # Index of the current parameter
        self.res = dict()  # Dictionary of results

    def begin_round(self, team1, team2, state):
        ball = Vector2D(GAME_WIDTH/2., GAME_HEIGHT/2.)
        
        # Player and ball postion (random)
        self.simu.state.states[(1, 0)].position = ball.copy()  # Shooter position
        self.simu.state.states[(1, 0)].vitesse = Vector2D()  # Shooter acceleration
        self.simu.state.ball.position = ball.copy()  # Ball position

        # Last step of the game
        self.last = self.simu.step

        # Set the current value for the current parameter
        for i, (key, values) in zip(self.param_id, self.params.items()):
            setattr(self.strategy, key, values[i])

    def update_round(self, team1, team2, state):
        me = StateFoot(state, 1, 0)
        # Stop the round if it is too long
        if state.step > self.last + self.max_round_step:
            #print(me.my_pos - me.center_point)
            self.simu.end_round()
        if me.my_pos.x >= GAME_WIDTH/2. + 36.:#15.
            #print(state.step - self.last)
            self.simu.end_round()


    def end_round(self, team1, team2, state):
        # A round ends when there is a goal
        me = StateFoot(state, 1, 0)
        if me.my_pos.x >= GAME_WIDTH/2. + 36.:#15.
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
            key = self.param_keys[self.param_id_id]
            if self.param_id[self.param_id_id] < len(self.params[key]) - 1:
                self.param_id[self.param_id_id] += 1
            else:
                self.simu.end_match()

        for i, (key, values) in zip(self.param_id, self.params.items()):
            print("{}: {}".format(key, values[i]), end="   ")
        print("Crit: {}   Cpt: {}".format(self.crit, self.cpt))

    def get_res(self):
        return self.res
