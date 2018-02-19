# coding: utf-8
from soccersimulator import SoccerTeam, Simulation, Strategy, show_simu, Vector2D
from soccersimulator.settings import GAME_WIDTH, GAME_HEIGHT


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
            team1 = SoccerTeam("Team 1")
            team2 = SoccerTeam("Team 2")
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
        #self.param_id = [self.params[key][0] for key in self.param_keys]
        self.param_id = [0] * len(self.params)  # Index of the parameter values
        self.param_id_id = 0  # Index of the current parameter
        self.res = dict()  # Dictionary of results

    def begin_round(self, team1, team2, state):
        dist = self.params['dist'][0]
        ball = Vector2D.create_random(low=0, high=1)
        ball.normalize().scale(dist)
        ball.y += GAME_HEIGHT/2.
    
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
            key = self.param_keys[self.param_id_id]
            #TODO mettre à 0 les valeurs precedentes
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

