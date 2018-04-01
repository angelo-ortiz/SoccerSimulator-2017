from ia.gs_optimisation import ParamSearchShoot, ParamSearchGoal, ParamSearchDribble, ParamSearchControle, ParamSearchPasse, ParamSearchReception
from ia.strategy_optimisation import ControlerTestStrategy, ShootTestStrategy, DribblerTestStrategy, GardienTestStrategy, PasseTestStrategy, ReceptionTestStrategy
import operator

#==============================================

dist = [i/1. for i in range(30,56,5)]
alpha = [i/100. for i in range(8,21, 4)]
beta = [i/100. for i in range(70, 111, 5)]

#expe = ParamSearchShoot(strategy=ShootTestStrategy(),
#        params={'dist': dist, 'alpha' : alpha, 'beta' : beta})

#==============================================

n_list = [i for i in range(4, 31)]
d_list = [r for r in range(10, 30)]

#expe = ParamSearchGoal(strategy=GardienTestStrategy(),
#                   params={'n': n_list, 'distance': d_list})

#==============================================

#power = [i/1000. for i in range(1030,1110)]
#power = [i/100. for i in range(103,111)]

#expe = ParamSearchControle(strategy=ControlerTestStrategy(),
#                   params={'power': power})

#==============================================

theta = [i for i in range(6, 31)]
power = [r/10 for r in range(10, 251)]

#expe = ParamSearchDribble(strategy=DribblerTestStrategy(),
#                   params={'theta': theta, 'power': power})

#==============================================

powerP = [r/10. for r in range(20, 31)]

#expe = ParamSearchPasse(strategy=PasseTestStrategy(),
#                   params={'power': powerP})

#==============================================

coeff = [r/100. for r in range(1, 120)]

expe = ParamSearchReception(strategy=ReceptionTestStrategy(),
                   params={'coeff': coeff})

expe.start()
print(expe.get_res())
mydict = expe.get_res()
liste = sorted(mydict.items(), key=operator.itemgetter(1), reverse=True)
for el in liste:
    if el[1] < 0.6:#> 0.9: #0.4: #< 0.9:
        break
    print(el)
