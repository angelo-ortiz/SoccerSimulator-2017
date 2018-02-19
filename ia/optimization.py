# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam, Simulation, Strategy, show_simu, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT


class ParamSearch(object):
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
            team1 = SoccerTeam("Team 1")
            team2 = SoccerTeam("Team 2")
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
        self.param_id_id = 0  # Index of the current parameter
        self.res = dict()  # Dictionary of results

    def begin_round(self, team1, team2, state):
        ball = Vector2D.create_random(low=0, high=1)
        ball.x *= GAME_WIDTH / 2
        ball.x += GAME_WIDTH / 2
        ball.y *= GAME_HEIGHT

        # Player and ball postion (random)
        self.simu.state.states[(2, 0)].position = ball.copy()  # Player position
        self.simu.state.states[(2, 0)].vitesse = Vector2D()  # Player acceleration
        self.simu.state.ball.position = ball.copy()  # Ball position

        # Last step of the game
        self.last = self.simu.step

        # Set the current value for the current parameter
        for i, (key, values) in zip(self.param_id, self.params.items()):
            setattr(self.strategy, key, values[i])

    def update_round(self, team1, team2, state):
        # Stop the round if it is too long
        me = StateFoot(state,1,0) #gardien
        if can_shoot(me):
            self.crit += 1  # Increment criterion
        if state.step > self.last + self.max_round_step:
            self.simu.end_round()

    def end_round(self, team1, team2, state):
        # A round ends when there is a goal
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
            elif self.param_id_id < len(self.params) - 1:
                self.param_id_id += 1
            else:
                self.simu.end_match()

        for i, (key, values) in zip(self.param_id, self.params.items()):
            print("{}: {}".format(key, values[i]), end="   ")
        print("Crit: {}   Cpt: {}".format(self.crit, self.cpt))

    def get_res(self):
        return self.res

