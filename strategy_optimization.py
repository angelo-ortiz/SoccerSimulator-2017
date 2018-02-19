from ia.optimization import ParamSearch
from ia.strategies import FonceurStrategy
from soccersimulator.settings import GAME_GOAL_HEIGHT, GAME_HEIGHT

n_list = [i for i in range(1, 50)]
d_list = [r for r in range(GAME_GOAL_HEIGHT/2, GAME_HEIGHT/2)]

expe = ParamSearch(strategy=GardienStrategy(),
                   params={'n': n_list, 'distance': d_list})
expe.start()
print(expe.get_res())