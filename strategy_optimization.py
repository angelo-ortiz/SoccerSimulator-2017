<<<<<<< HEAD
from ia.optimization import ParamSearchShoot
from ia.strategies import ShootTestStrategy
import operator

#dist = [i/10. for i in range(200,201)]
dist = [i/1. for i in range(30,56,5)]
#alpha = [i/100. for i in range(5,7)]
alpha = [i/100. for i in range(8,21, 4)]
#beta = [i/100. for i in range(18,20)]
beta = [i/100. for i in range(70, 111, 5)]
expe = ParamSearchShoot(strategy=ShootTestStrategy(),
        params={'dist': dist, 'alpha' : alpha, 'beta' : beta})
expe.start()
print(expe.get_res())
mydict = expe.get_res()
liste = sorted(mydict.items(), key=operator.itemgetter(1), reverse=True)
for el in liste:
    if el[1] < 0.9:
        break
    print(el)
=======
from ia.optimization import ParamSearch
from ia.strategies import FonceurStrategy
from soccersimulator.settings import GAME_GOAL_HEIGHT, GAME_HEIGHT

n_list = [i for i in range(1, 50)]
d_list = [r for r in range(GAME_GOAL_HEIGHT/2, GAME_HEIGHT/2)]

expe = ParamSearch(strategy=GardienStrategy(),
                   params={'n': n_list, 'distance': d_list})
expe.start()
print(expe.get_res())
>>>>>>> 03f05e031d9e8e684cecf33199096209b367564d
