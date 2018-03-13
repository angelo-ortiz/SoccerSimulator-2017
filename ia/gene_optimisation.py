# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam
from ia.strategies import FonceurStrategy, GardienStrategy, AttaquantStrategy
from functools import total_ordering
from math import pi as PI, sqrt
import random
import pickle

def setCounters(simu, team1, team2):
    """
        Met a jour les compteurs des deux vecteurs qui
        ont participe au dernier match avec les regles
        connues du football (buts et points)
    """
    team1.fg += simu.get_score_team(1)
    team2.fg += simu.get_score_team(2)
    team1.ag += team2.fg
    team2.ag += team1.fg
    if team1.fg > team2.fg:
        team1.pts += 3
    elif team1.fg == team2.fg:
        team1.pts += 1
        team2.pts += 1
    else:
        team2.pts += 3

def setCountersSolo(simu, team1, rev):
    """
        Met a jour les compteurs des deux vecteurs qui
        ont participe au dernier match avec les regles
        connues du football (buts et points)
    """
    if rev: i, j = 2, 1
    else: i, j = 1, 2
    team1.fg += simu.get_score_team(i)
    team1.ag += simu.get_score_team(j)
    if team1.fg > team1.ag:
        team1.pts += 3
    elif team1.fg == team1.ag:
        team1.pts += 1

def getDistinctTuple(low=0, high=30):
    """
        Renvoie un couple d'entiers distincts compris
        entre low (inclus) et high (exlu)
    """
    i = random.randrange(low, high)
    while True:
        j = random.randrange(low, high)
        if i != j: break
    return i, j

def savePath(fn):
    """
        Renvoie le chemin d'acces absolu du fichier 
        passe en parametre pour la serialisation
        d'un dictionnaire de parametres
    """
    from os.path import dirname, realpath, join
    return join(dirname(dirname(realpath(__file__))),"parameters",fn)

@total_ordering
class dictParams(object):
    def __init__(self):
        self.params = {'alphaShoot': 0., 'betaShoot': 0., 'powerDribble': 0., \
                'tempsI': 0, 'angleDribble': 0., 'rayInter': 0., 'distShoot': 0., \
                'rayDribble': 0., 'angleGardien': 0., 'coeffAD': 0., \
                'distSortie': 0., 'raySortie': 0., 'controleMT': 0., \
                'profDeg': 0., 'amplDeg': 0., 'decalX': 0., 'decalY': 0., \
                'distAttaque': 0., 'controleAttaque': 0., 'distMontee': 0.}
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
        return {'alphaShoot': (0.,1.), 'betaShoot': (0.4,1.2), 'powerDribble': (0.,6.), \
                'tempsI': (0,30), 'angleDribble': (0.,PI/2.), 'rayInter': (0.,40.), \
                'distShoot': (10.,40.), 'distDribble': (0.,50.), \
                'angleGardien':  (sqrt(2.)/2.,1.), 'coeffAD': (0.7,1.5), \
                'distSortie': (40.,70.), 'raySortie': (0.,25.), 'controleMT': (0.,2.), \
                'profDeg': (10.,70.), 'amplDeg': (0.,40.), 'decalX': (0.,50.), \
                'decalY': (0.,40.), 'distAttaque': (40.,70.), 'controleAttaque': (0., 1.2) \
                'distMontee': (40.,80.)}

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
        """
            Affiche a l'ecran tous les parametres du vecteur
            et les resultats de l'experience
        """
        for p in parameters:
            print(p, ":", self.params[p])
        print("points : ", self.pts)
        print("fg : ", self.fg)
        print("ag : ", self.ag)


class GKStrikerTeam(object):
    def __init__(self, size=20, keep=0.5, coProb=0.7, mProb=0.01):
        self.name = "GKStrikerTeam"
        self.team = None
        self.size = size # nombre de vecteurs
        self.keep = keep # pourcentage de conservation
        self.coProb = coProb # probabilite de croisement
        self.mProb = mProb # probabilite de mutation
        self.gk = GardienStrategy() # strategie goalkeeper (gk)
        self.st = AttaquantStrategy() #FonceurStrategy() # strategie striker (st)
        self.vectors = [] # vecteurs de parametres
        self.gk_params = ['tempsI', 'rayInter', 'distSortie', 'raySortie', \
                'profDeg', 'amplDeg', 'distMontee'] # parametres du gk
        self.st_params = ['alphaShoot', 'betaShoot', 'angleDribble', \
                'powerDribble', 'distShoot', 'rayDribble', 'angleGardien', \
                'coeffAD', 'controleMT', 'decalX', 'decalY', 'distAttaque', \
                'controleAttaque'] # parametres du st

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
            self.gk.dico[p] = params[p]
        for p in self.st_params:
            self.st.dico[p] = params[p]
        self.team = SoccerTeam("GKStriker")
        self.team.add(self.gk.name, self.gk)
        self.team.add(self.st.name, self.st)
        return self.team

    def sortVectors(self):
        """
            Trie les vecteurs de parametres dans l'ordre decroissant
            selon les points obtenuss
        """
        self.vectors.sort(reverse=True)

    def getBestTeam(self):
        """
            Renvoie l'equipe qui a mieux reussi les matches
        """
        self.sortVectors()
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
        vk = dictParams()
        pList = self.gk_params + self.st_params
        index = random.randrange(0, len(pList))
        for l in range(index):
            vk.params[pList[l]] = vi.params[pList[l]]
        for l in range(index,len(pList)):
            vk.params[pList[l]] = vj.params[pList[l]]
        self.vectors[k] = vk

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
        self.sortVectors()
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

    def gkDict(self):
        """
            Renvoie le sous-dictionnaire du meilleur vecteur
            de parametres compose uniquement de ceux contenus
            dans l'attribut gk_params
            Hypothese : sortVectors() doit avoir ete appele 
            auparavant 
        """
        gk_dict = self.vectors[0].params
        return {k:gk_dict[k] for k in self.gk_params if k in gk_dict}

    def stDict(self):
        """
            Renvoie le sous-dictionnaire du meilleur vecteur
            de parametres compose uniquement de ceux contenus
            dans l'attribut st_params
            Hypothese : sortVectors() doit avoir ete appele 
            auparavant 
        """
        st_dict = self.vectors[0].params
        return {k:st_dict[k] for k in self.st_params if k in st_dict}

    def save(self, fn_st="st_dico.pkl", fn_gk="gk_dico.pkl"):
        """
            Sauvegarde le dictionnaire de parametres de chaque joueur
            dans des fichiers dans le repertoire 'parameters'
        """
        self.sortVectors()
        with open(savePath(fn_st),"wb") as f:
            pickle.dump(self.stDict(),f,protocol=pickle.HIGHEST_PROTOCOL)
        with open(savePath(fn_gk),"wb") as f:
            pickle.dump(self.gkDict(),f,protocol=pickle.HIGHEST_PROTOCOL)
