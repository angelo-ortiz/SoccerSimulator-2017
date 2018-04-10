# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam
from ia.strategies import AttaquantStrategy, GardienStrategy
from ia.strategies import Gardien2v2Strategy, Attaquant2v2Strategy, Fonceur1v1Strategy
from ia.gene_optimisation import savePath
from ia.strategies_machlearning import LearningStrategy
from math import pi as PI, sqrt
import random
import pickle

class LearningTeam(object):
    def __init__(self, Qmatrix=None):
        self.name = "LearningTeam"
        self.team = So
        super(LearningTeam, self).__init__(name="LearningTeam")
        self.Qmatrix = Qmatrix
        self.add("Student1", LearningStrategy(self.Qmatrix))
        self.add("Student2", LearningStrategy(self.Qmatrix))
        
    def compute_rewards():
        """
        """
        return None




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
        keep*100% superieur, et modifie le reste avec une
        mutation, un croisement des meilleurs scores ou
        des valeurs aleatoires (deux vecteurs)
        """
        self.sortVectors()
        size = len(self.vectors)
        nKeep = int(size * self.keep)
        for k in range(nKeep, size-2):
            while True:
                i, j = getDistinctTuple(high=nKeep)
                r = random.random()
                if r < self.mProb:
                    self.mutation(i, j, k)
                    break
                elif r < self.coProb:
                    self.crossover(i, j, k)
                    break
        pList = self.paramsList()
        for k in range(size-2, size):
            self.vectors[k] = dictParams()
        for k in range(size-2, size):
            self.vectors[k].random(pList)


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
        if self.playerParams[i] is None:
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
            playerStrats=[Gardien2v2Strategy(), Attaquant2v2Strategy(), None, None], \
            playerParams=[GKStrikerTeam.gk_params(), GKStrikerTeam.st_params(), [], []], \
            size=size, keep=keep, coProb=coProb, mProb=mProb)

    @classmethod
    def gk_params(cls):
        return ['tempsI', 'rayInter', 'distSortie', 'raySortie', \
                'profDeg', 'amplDeg', 'powerDeg', 'tempsContr']

    @classmethod
    def st_params(cls):
        return ['alphaShoot', 'betaShoot', 'angleDribble', 'powerDribble', \
                'distShoot', 'rayDribble', 'angleGardien', 'coeffAD', \
                'controleMT', 'decalX', 'decalY', 'distAttaque', \
                'controleAttaque', 'distDefZone', 'powerPasse', 'thetaPasse',\
                'distDemar', 'rayPressing', 'rayRecept', 'angleRecept', \
                'rayReprise', 'angleReprise', 'coeffPushUp', 'distPasse', \
                'distMontee', 'angleInter', 'coeffDef']

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
        Sauvegarde le dictionnaire de parametres du gardien
        et de l'attaquant dans des fichiers dans le repertoire
        'parameters'
        """
        return super(GKStrikerTeam, self).save([fn_gk, fn_st, None, None])



class GKStrikerMixTeam(GKStrikerTeam):
    def __init__(self, size=20, keep=0.5, coProb=0.7, mProb=0.01):
        super(GKStrikerMixTeam, self).__init__(size=size, keep=keep, \
            coProb=coProb, mProb=mProb)

    def getTeam(self, i):
        """
        Renvoie l'equipe composee des strategies contenues
        dans l'instance avec l'i-ieme vecteur de parametres
        applique a toutes les deux i.e. une SoccerTeam dont
        les deux joueurs ont les meme parametres
        """
        self.team = SoccerTeam(self.name)
        params = self.vectors[i].params
        for i in range(2):
            for p in self.playerParams[i]:
                self.playerStrats[0].dico[p] = params[p] # params du gk
                self.playerStrats[1].dico[p] = params[p] # params du st
        self.team.add(self.playerStrats[0].name, self.playerStrats[0])
        self.team.add(self.playerStrats[1].name, self.playerStrats[1])
        return self.team



class STTeam(GeneTeam):
    def __init__(self, size=20, keep=0.5, coProb=0.7, mProb=0.01):
        super(STTeam, self).__init__(name="STTeam", \
            playerStrats=[Fonceur1v1Strategy(), None, None, None], \
            playerParams=[GKStrikerTeam.gk_params(), GKStrikerTeam.st_params(), [], []], \
            size=size, keep=keep, coProb=coProb, mProb=mProb)

    def stDict(self):
        """
        Renvoie le sous-dictionnaire du meilleur vecteur de
        parametres compose uniquement de ceux concernant
        l'attaquant
        Hypothese : sortVectors() doit avoir ete appele
        auparavant
        """
        return super(STTeam, self).playerDict(0)

    def getTeam(self, i):
        """
        Renvoie l'equipe composee de la strategie contenue
        dans l'instance avec l'i-ieme vecteur de parametres
        i.e. une SoccerTeam d'un joueur ayant les deux types
        de parametres
        """
        self.team = SoccerTeam(self.name)
        params = self.vectors[i].params
        for i in range(2):
            for p in self.playerParams[i]:
                self.playerStrats[0].dico[p] = params[p] # params du st
        self.team.add(self.playerStrats[0].name, self.playerStrats[0])
        return self.team

    def save(self, fn_gk="fonceur_gk_dico.pkl", fn_st="fonceur_st_dico.pkl"):
        """
        Sauvegarde les deux dictionnaires de parametres utilises
        par le fonceur dans des fichiers dans le repertoire
        'parameters'
        """
        return super(STTeam, self).save([fn_gk, fn_st, None, None])
