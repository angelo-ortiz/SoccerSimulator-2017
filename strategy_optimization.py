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
