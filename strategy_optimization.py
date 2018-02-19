from ia.optimization import ParamSearchShoot
from ia.strategies import ShootTestStrategy

dist = [i/10. for i in range(200,550)]
alpha = [i/100. for i in range(5,50)]
beta = [i/100. for i in range(20)]
expe = ParamSearchShoot(strategy=ShootTestStrategy(),
        params={'dist': dist, 'alpha' : alpha, 'beta' : beta})
expe.start()
print(expe.get_res())

