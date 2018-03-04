from ia.gs_optimisation import ParamSearchShoot, ParamSearchGoal, ParamSearchDribble
from ia.strategies import FonceurStrategy
from ia.strategy_optimisation import ShootTestStrategy, DribblerTestStrategy, GardienTestStrategy
import operator

dist = [i/1. for i in range(30,56,5)]
alpha = [i/100. for i in range(8,21, 4)]
beta = [i/100. for i in range(70, 111, 5)]

#expe = ParamSearchShoot(strategy=ShootTestStrategy(),
#        params={'dist': dist, 'alpha' : alpha, 'beta' : beta})

#==============================================
n_list = [i for i in range(4, 31)]
d_list = [r for r in range(10, 30)]

expe = ParamSearchGoal(strategy=GardienTestStrategy(),
                   params={'n': n_list, 'distance': d_list})

#==============================================
power = [i/100. for i in range(90,141)]

#expe = ParamSearchControle(strategy=ControlerTestStrategy(),
#                   params={'power': power})

#==============================================
theta = [i for i in range(6, 31)]
power = [r/10 for r in range(10, 251)]

#expe = ParamSearchDribble(strategy=DribblerTestStrategy(),
#                   params={'theta': theta, 'power': power})

expe.start()
print(expe.get_res())
mydict = expe.get_res()
liste = sorted(mydict.items(), key=operator.itemgetter(1), reverse=False)
for el in liste:
    if el[1] > 0.4:#> 0.9: #0.4: #< 0.9:
        break
    print(el)
