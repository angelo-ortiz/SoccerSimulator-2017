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
    Met a jour les compteurs des deux vecteurs qui ont
    participe au dernier match avec les regles connues
    du football (buts et points)
    """
    gt1 = simu.get_score_team(1)
    gt2 = simu.get_score_team(2)
    if gt1 > gt2:
        team1.pts += 3
    elif gt1 == gt2:
        team1.pts += 1
        team2.pts += 1
    else:
        team2.pts += 3
    team1.fg += gt1
    team2.fg += gt2
    team1.ag += gt2
    team2.ag += gt1

def setCountersSolo(simu, team1, rev):
    """
    Met a jour les compteurs des deux vecteurs qui ont
    participe au dernier match avec les regles connues
    du football (buts et points)
    """
    if rev: i, j = 2, 1
    else: i, j = 1, 2
    fg = simu.get_score_team(i)
    ag = simu.get_score_team(j)
    if fg > ag:
        team1.pts += 3
    elif fg == ag:
        team1.pts += 1
    team1.fg += fg
    team1.ag += ag

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

def savePath(fn):
    """
    Renvoie le chemin d'acces absolu du fichier passe en
    parametre pour la serialisation d'un dictionnaire de
    parametres
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
                'distAttaque': 0., 'controleAttaque': 0., 'distMontee': 0., \
                'distDefZone': 0.}
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
                'distShoot': (10.,40.), 'rayDribble': (0.,50.), \
                'angleGardien':  (sqrt(2.)/2.,1.), 'coeffAD': (0.7,1.5), \
                'distSortie': (40.,70.), 'raySortie': (0.,25.), 'controleMT': (0.8,2.), \
                'profDeg': (10.,70.), 'amplDeg': (0.,40.), 'decalX': (0.,50.), \
                'decalY': (0.,40.), 'distAttaque': (40.,70.), 'controleAttaque': (0., 1.2), \
                'distMontee': (40.,80.), 'distDefZone': (10.,40.)}

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
        Renvoie vrai ssi la valeur du parametre p est bien valide,
        i.e. comprise dans ses limites definies
        """
        val = self.params[p]
        limits = dictParams.limits()
        return val >= limits[p][0] and val <= limits[p][1]

    def restart(self):
        """
        Remet a zero tous les compteurs du vecteur, a savoir
        le nombre de points, le nombre de buts marques et le
        nombre de buts encaisses
        """
        self.pts = 0
        self.fg = 0
        self.ag = 0

    def printParams(self, parameters):
        """
        Affiche a l'ecran tous les parametres du vecteur et
        les resultats de l'experience
        """
        for p in parameters:
            print(p, ":", self.params[p])
        print("------------------------")
        print("points : ", self.pts)
        print("fg : ", self.fg)
        print("ag : ", self.ag)



class GeneTeam(object):
    def __init__(self, name="GeneTeam", playerStrats=[None]*4, \
                 playerParams=[[]]*4, size=20, keep=0.5, coProb=0.7, mProb=0.01):
        self.name = name
        self.team = None
        self.size = size # nombre de vecteurs
        self.keep = keep # pourcentage de conservation
        self.coProb = coProb # probabilite de croisement
        self.mProb = mProb # probabilite de mutation
        self.playerStrats = playerStrats # strategie de chaque joueur
        self.playerParams = playerParams # parametres de chaque joueur
        self.vectors = [] # vecteurs de parametres

    def paramsList(self):
        """
        Renvoie la liste de tous les parametres a optimiser
        """
        return [p for playParams in self.playerParams for p in playParams]

    def start(self):
        """
        Cree et randomise tous les vecteurs
        """
        pList = self.paramsList()
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
        i.e. une SoccerTeam
        """
        self.team = SoccerTeam(self.name)
        params = self.vectors[i].params
        for i in range(len(self.playerStrats)):
            if self.playerStrats[i] is None: continue
            for p in self.playerParams[i]:
                self.playerStrats[i].dico[p] = params[p]
            self.team.add(self.playerStrats[i].name, self.playerStrats[i])
        return self.team

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

    def sortVectors(self):
        """
        Trie les vecteurs de parametres dans l'ordre decroissant
        selon les points obtenuss
        """
        self.vectors.sort(reverse=True)

    def crossover(self, i, j, k):
        """
        Fait un croisement entre les vecteurs i- et j-ieme et
        le met dans le k-ieme vecteur
        """
        vi = self.vectors[i]
        vj = self.vectors[j]
        vk = dictParams()
        pList = self.paramsList()
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
        Fait une mutation entre les vecteurs i- et j-ieme dans
        le vecteur k-ieme, ie un croisement avec du bruit sur
        l'un des parametres
        """
        self.crossover(i, j, k)
        pList = self.paramsList()
        pl = random.randrange(0, len(pList))
        self.addNoise(k, pList[pl])

    def update(self):
        """
        Garde les meilleurs resultats, qui representent le
        keep*100% superieur, et modifie le reste avec soit une
        mutation, soit un croisement des meilleurs scores
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
        pList = self.paramsList()
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

    def playerDict(self, i):
        """
        Renvoie le sous-dictionnaire du meilleur vecteur de
        parametres compose uniquement de ceux concernant
        le i-ieme joueur
        Hypothese : sortVectors() doit avoir ete appele
        auparavant
        """
        if self.playerStrats[i] is None:
            return None
        play_dict = self.vectors[0].params
        return {k:play_dict[k] for k in self.playerParams[i] if k in play_dict}

    def save(self, filenames=[None]*4):
        """
        Sauvegarde le dictionnaire de parametres de chaque joueur
        dans des fichiers dans le repertoire 'parameters'
        """
        self.sortVectors()
        for i in range(len(filenames)):
            if filenames[i] is None: continue
            play_dict = self.playerDict(i)
            if play_dict is None: continue
            with open(savePath(filenames[i]),"wb") as f:
                pickle.dump(play_dict,f,protocol=pickle.HIGHEST_PROTOCOL)



class GKStrikerTeam(GeneTeam):
    def __init__(self, size=20, keep=0.5, coProb=0.7, mProb=0.01):
        super(GKStrikerTeam, self).__init__(name="GKStrikerTeam", \
            playerStrats=[GardienStrategy(), AttaquantStrategy(), None, None], \
            playerParams=[GKStrikerTeam.gk_params(), GKStrikerTeam.st_params(), [], []], \
            size=size, keep=keep, coProb=coProb, mProb=mProb)

    @classmethod
    def gk_params(cls):
        return ['tempsI', 'rayInter', 'distSortie', 'raySortie', \
                'profDeg', 'amplDeg', 'distMontee']

    @classmethod
    def st_params(cls):
        return ['alphaShoot', 'betaShoot', 'angleDribble', 'powerDribble', \
                'distShoot', 'rayDribble', 'angleGardien', 'coeffAD', \
                'controleMT', 'decalX', 'decalY', 'distAttaque', \
                'controleAttaque', 'distDefZone']

    def gkDict(self):
        """
        Renvoie le sous-dictionnaire du meilleur vecteur de
        parametres compose uniquement de ceux concernant
        le gardien
        Hypothese : sortVectors() doit avoir ete appele
        auparavant
        """
        return super(GKStrikerTeam, self).playerDict(0)

    def stDict(self):
        """
        Renvoie le sous-dictionnaire du meilleur vecteur de
        parametres compose uniquement de ceux concernant
        l'attaquant
        Hypothese : sortVectors() doit avoir ete appele
        auparavant
        """
        return super(GKStrikerTeam, self).playerDict(1)

    def save(self, fn_gk="gk_dico.pkl", fn_st="st_dico.pkl"):
        """
        Sauvegarde le dictionnaire de parametres du gardien et de
        l'attaquant dans des fichiers le repertoire 'parameters'
        """
        return super(GKStrikerTeam, self).save([fn_gk, fn_st, None, None])
