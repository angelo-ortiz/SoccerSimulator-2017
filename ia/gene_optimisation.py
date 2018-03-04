# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam
from ia.strategies import FonceurStrategy, GardienStrategy, AttaquantStrategy
from functools import total_ordering
import random
import copy
import math

def setCounters(simu, team1, team2):
    """
        Met a jour les compteurs des deux vecteurs qui 
        ont participe au dernier match avec les regles 
        connues du football (buts et points)
    """
    team1.fg = simu.get_score_team(1)
    team2.fg = simu.get_score_team(2)
    team1.ag, team2.ag = team2.fg, team1.fg
    if team1.fg > team2.fg:
        team1.pts += 3
    elif team1.fg == team2.fg:
        team1.pts += 1
        team2.pts += 1
    else:
        team2.pts += 3

def setCountersSolo(simu, team1):
    """
        Met a jour les compteurs des deux vecteurs qui 
        ont participe au dernier match avec les regles 
        connues du football (buts et points)
    """
    team1.fg = simu.get_score_team(1)
    team1.ag = simu.get_score_team(2)
    if team1.fg > team1.ag:
        team1.pts += 3
    elif team1.fg == team1.ag:
        team1.pts += 1

def getDistinctTuple(low=0, high=30):
    """
    Renvoie un couple d'entiers distincts compris entre 
    low (inclus) et high (exlu)
    """
    i = random.randrange(low, high)
    while True:
        j = random.randrange(low, high)
        if i != j: break
    return i, j

@total_ordering
class dictParams(object):
    def __init__(self):
        self.params = {'alpha': 0., 'beta': 0., 'powerDribble': 0.,'tempsI': 0, 'angleDribble': 0., \
                """'n': 0,""" 'distInter': 0., 'distShoot': 0., 'distDribble': 0., 'angleGardien': 0., \
                       'coeffAD': 0.}
        self.pts = 0 # le nombre de points obtenus (V,N,D) = (3,1,0)
        self.fg = 0     # le nombre de buts marques
        self.ag = 0     # le nombre de buts encaisses

    def __lt__(self, other):
        return ((self.pts, self.fg - self.ag, self.fg) < \
                (other.pts, other.fg - other.ag, other.fg))
    
    def __eq__(self, other):
        return ((self.pts, self.fg - self.ag, self.fg) == \
                (other.pts, other.fg - other.ag, other.fg))

    @classmethod
    def limits(cls):
        """
            Renvoie un dictionnaire avec les bornes de chaque 
            parametre
        """
        return {'alpha': (0.,1.), 'beta': (0.4,1.), 'powerDribble': (0.,6.),'tempsI': (0,50), \
                'angleDribble': (-math.pi/2.,math.pi/2.), 'n': (0,50), 'distInter': (0., 40.), \
                'distShoot': (0., 70.), 'distDribble': (0., 50.), 'angleGardien':  (0.,math.sqrt(2.)/2.), \
'coeffAD': (0.7, 1.5)}
    
    def random(self, parameters):
        """
            Randomise tous les parametres du vecteur avec des 
            valeurs comprises dans les limites acceptables
        """
        limits = dictParams.limits()
        for p in parameters:
            pLimits = limits[p]
            self.params[p] = random.uniform(pLimits[0], pLimits[1])

    def isValid(self, p):
        """
            Renvoie vrai ssi la valeur du parametre p est 
            bien valide, ie comprise dans ses limites definies
        """
        val = self.params[p]
        limits = dictParams.limits()
        return val >= limits[p][0] and val <= limits[p][1]

    def restart(self):
        """
            Remet a zero tous les compteurs du vecteur, 
            a savoir, le nombre de points, le nombre de buts 
            marques et le nombre de buts encaisses
        """
        self.pts = 0
        self.fg = 0
        self.ag = 0
        
    def printParams(self, parameters):
        for p in parameters:
            print(p, ":", self.params[p])
        print("points : ", self.pts)
        print("fg : ", self.fg)
        print("ag : ", self.ag)


class GKStrikerTeam(object):
    def __init__(self, size=20, keep=0.4, coProb=0.7, mProb=0.08):
        self.name = "GKStrikerTeam"
        self.team = None
        self.size = size # nombre de vecteurs
        self.keep = keep # pourcentage de conservation
        self.coProb = coProb # probabilite de croisement
        self.mProb = mProb # probabilite de mutation
        self.gk = GardienStrategy() # strategie goalkeeper (gk)
        self.st = AttaquantStrategy() #FonceurStrategy() # strategie striker (st)
        self.vectors = [] # vecteurs de parametres
        self.gk_params = ['tempsI', 'distInter'] # parametres du gk
        self.st_params = ['alpha', 'beta', 'angleDribble', 'powerDribble', 'distShoot', 'distDribble', 'angleGardien', 'coeffAD'] # parametres du st

    def start(self):
        """
            Cree et randomise tous les vecteurs
        """
        pList = self.gk_params + self.st_params
        for i in range(self.size):
            self.vectors.append(dictParams())
        for v in self.vectors:
            v.random(pList)

    def restart(self):
        """
            Remet a zero tous les compteurs de chaque vecteur
        """
        for v in self.vectors:
            v.restart()

    def getTeam(self, i):
        """
            Renvoie l'equipe composee des strategies contenues 
            dans l'instance avec l'i-ieme vecteur de parametres, 
            ie une SoccerTeam
        """
        params = self.vectors[i].params
        for p in self.gk_params:
            self.gk.dictGK[p] = params[p]
        for p in self.st_params:
            self.st.dictST[p] = params[p]
        self.team = SoccerTeam("GKStriker")
        self.team.add(self.gk.name, self.gk)
        self.team.add(self.st.name, self.st)
        return self.team

    def getBestTeam(self):
        """
            Renvoie l'equipe qui reussit le mieux les matches
        """
        self.vectors.sort()
        return self.getTeam(0)

    def getVector(self, i):
        """
            Renvoie l'i-ieme vecteur de parametres, ie un dictParams
        """
        return self.vectors[i]

    def crossover(self, i, j, k):
        """
            Fait un croisement entre les vecteurs i- et j-ieme 
            et le met dans le k-ieme vecteur
        """
        vi = self.vectors[i]
        vj = self.vectors[j]
        vk = copy.deepcopy(vi)
        pList = self.gk_params + self.st_params
        index = random.randrange(0, len(pList))
        for l in range(index):
            vk.params[pList[l]] = vj.params[pList[l]]

    def addNoise(self, i, p):
        """
            Ajoute du bruit au parametre p de l'i-ieme vecteur 
            de parametres
        """
        val = self.vectors[i].params[p]
        while True:
            valNoise = val * random.uniform(0.9,1.1)
            if valNoise == val: continue
            self.vectors[i].params[p] = valNoise
            if self.vectors[i].isValid(p):
                break
    
    def mutation(self, i, j, k):
        """
            Fait une mutation entre les vecteurs i- et j-ieme 
            dans le vecteur k-ieme, ie un croisement avec du 
            bruit sur l'un des parametres
        """
        self.crossover(i, j, k)
        pList = self.gk_params + self.st_params
        pl = random.randrange(0, len(pList))
        self.addNoise(k, pList[pl])

    def update(self):
        """
            Garde les meilleurs resultats, qui representent 
            le keep*100% superieur, et modifie le reste avec 
            soit une mutation, soit un croisement des meilleurs
            scores
        """
        self.vectors.sort(reverse=True)
        size = len(self.vectors)
        nKeep = int(size * self.keep)
        for k in range(nKeep, size):
            while True:
                i, j = getDistinctTuple(high=nKeep)
                r = random.random()
                if r < self.mProb:
                    self.mutation(i, j, k)
                    break
                elif r < self.coProb:
                    self.crossover(i, j, k)
                    break

    def printVectors(self, nVect):
        """
            Affiche les nVect premiers vecteurs de parametres 
        """
        print(self.name)
        pList = self.gk_params + self.st_params
        for i in range(nVect):
            print(i+1, "/ ", end='')
            self.vectors[i].printParams(pList)
            print()

    def printAllVectors(self):
        """
            Affiche tous les vecteurs de parametres
        """
        self.printVectors(len(self.vectors))
        print("==================================================")
