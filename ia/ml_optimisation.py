# coding: utf-8
from __future__ import print_function, division
from soccersimulator import SoccerTeam, Simulation, show_simu
from ia.tools import StateFoot, nearest
from ia.strategies import loadPath
from ia.gene_optimisation import savePath
from ia.ml_behaviour import attDict, defDict
from ia.ml_strategies import Attaquant2v2Strategy, Defenseur2v2Strategy
import numpy as np
import random
import pickle

class LearningState(object):

    difference = 10.

    def __init__(self, stateFoot):
        stateFoot = stateFoot
        self.distances = dict()
        self.distances['JB'] = stateFoot.distance(stateFoot.ball_pos)
        #self.distances['JmG'] = stateFoot.distance(stateFoot.my_goal)
        self.distances['JoG'] = stateFoot.distance(stateFoot.opp_goal)
        #self.distances['BmG'] = stateFoot.distance_ball(stateFoot.my_goal)
        #self.distances['BoG'] = stateFoot.distance_ball(stateFoot.opp_goal)
        nearestOpp = stateFoot.opponent_nearest_ball.position
        self.distances['JnO'] = stateFoot.distance(nearestOpp)
        #self.distances['nOoG'] = nearestOpp.distance(stateFoot.opp_goal)
        nearestTm = nearest(stateFoot.my_pos, stateFoot.teammates)
        nearestOppTm = nearest(nearestTm, stateFoot.opponents)
        self.distances['TmnO'] = nearestTm.distance(nearestOppTm)
        #self.distances['nTmoG'] = nearestTm.distance(stateFoot.opp_goal)
        #self.distances['nOnTmoG'] = nearestOppTm.distance(stateFoot.opp_goal)
        self.distances['nJnT'] = stateFoot.distance(nearestTm)
        self.ballDir = stateFoot.attacking_vector.dot(stateFoot.ball_speed.copy().normalize())

    def __eq__(self, other):
        if not isinstance(other, LearningState): return False
        if self.ballDir * other.ballDir == 0. and self.ballDir + other.ballDir != 0.:
            return False
        if self.ballDir * other.ballDir < 0.: return False
        for k, dist in self.distances.items():
            if abs(dist - other.distances[k]) >= self.difference:
                return False
        return True

    def __hash__(self):
        return hash(str(self.distances) + str(self.ballDir))

    def __str__(self):
        return "LearningState(distances={}, ballDir={})".format(self.distances, self.ballDir)

class LearningTeam(object):

    actionsDict = {'Attaquant2v2': len(attDict), 'Defenseur2v2': len(defDict)}

    def __init__(self, numPlayers=2, playerStrats=[None]*4, alpha=0.6, gamma=0.8, eps=0.2, oppList=[],
                 numIter=10, numMatches=3, graphical=False):
        self.name = "LearningTeam"
        self.team = None
        self.numPlayers = numPlayers
        self.playerStrats = playerStrats
        self.playerQTables = []
        self.alpha = alpha
        self.gamma = gamma
        self.eps = eps
        self.oppList = oppList
        self.numIter = numIter
        self.numMatches = numMatches
        self.graphical = graphical
        self.currMatch = [0,0,True,0] # iter, opp, left_side, match
        self.simu = None
        self.prevState = None
        self.currState = None
        self.idTeam = 0
        self.count = [0] * self.numPlayers

    def initialize(self, filenames=None):
        """
        """
        if filenames is not None:
            for fn in filenames:
                if fn is not None:
                    with open(loadPath(fn), "rb") as f:
                        self.playerQTables.append(pickle.load(f))
        else:
            for i in range(self.numPlayers):
                self.playerQTables.append(dict())

    def getTeam(self):
        """
        Renvoie l'equipe composee des strategies contenues
        dans l'instance avec les Q-Tables associees
        """
        self.team = SoccerTeam(self.name)
        for i in range(self.numPlayers):
            self.playerStrats[i].qTable = self.playerQTables[i]
            self.team.add(self.playerStrats[i].name, self.playerStrats[i])
        return self.team

    def q(self, idPlayer, state, action=None):
        """
        """
        if state not in self.playerQTables[idPlayer]:
            self.count[idPlayer] += 1
            self.playerQTables[idPlayer][state] = np.zeros(self.actionsDict[self.playerStrats[idPlayer].name])
        if action is None:
            return self.playerQTables[idPlayer][state]
        return self.playerQTables[idPlayer][state][action]

    def chooseAction(self, idPlayer, state):
        """
        """
        if random.uniform(0, 1) < self.eps:
            return random.choice(list(range(self.actionsDict[self.playerStrats[idPlayer].name])))
        # return np.argmax(self.q(idPlayer, state))
        qT = self.q(idPlayer, state)
        indices = np.argwhere(qT == np.amax(qT)).flatten().tolist()
        return random.choice(indices)

    def computeReward(self):
        """
        """
        control = StateFoot(self.prevState, self.idTeam, 0, self.numPlayers).team_controls_ball()
        if control == True:
            rew = 1
        elif control == False:
            rew = -1
        else:
            rew = 0
        if self.prevState.goal == self.idTeam:
            rew += 100
        elif self.prevState.goal != 0:
            rew -= 100
        return rew

    def updateAction(self, idPlayer, action):
        """
        """
        prevState = LearningState(StateFoot(self.prevState, self.idTeam, idPlayer, self.numPlayers))
        currState = LearningState(StateFoot(self.currState, self.idTeam, idPlayer, self.numPlayers))
        if action is not None:
            prevQ = self.q(idPlayer, prevState, action)
            rew = self.computeReward()
            self.q(idPlayer, prevState)[action] = \
                    prevQ + self.alpha * (self.computeReward() + self.gamma * np.max(self.q(idPlayer, currState)) - prevQ)
        self.playerStrats[idPlayer].action = self.chooseAction(idPlayer, currState)

    def updateAll(self):
        """
        """
        for idPlayer in range(self.numPlayers):
            self.updateAction(idPlayer, self.playerStrats[idPlayer].action)

    def start(self):
        """
        """
        right, left = self.getTeam(), self.oppList[self.currMatch[1]]
        self.idTeam = 2
        if self.currMatch[2]:
            left, right = right, left
            self.idTeam = 1
        self.simu = Simulation(left, right)
        self.simu.listeners += self
        if self.graphical:
            show_simu(self.simu)
        else:
            self.simu.start()

    def update_round(self, left, right, state):
        """
        """
        self.prevState = self.currState
        self.currState = state
        if self.prevState is not None:
            self.updateAll()

    def end_match(self, left, right, state):
        """
        """
        if self.currMatch[3] < self.numMatches - 1:
            self.currMatch[3] += 1
        elif self.currMatch[2]:
            self.currMatch[3] = 0
            self.currMatch[2] = False
            # print("Fin aller")
        elif self.currMatch[1] < len(self.oppList) - 1:
            self.currMatch[3] = 0
            self.currMatch[2] = True
            self.currMatch[1] += 1
            # print("Fin retour")
        elif self.currMatch[0] < self.numIter - 1:
            self.currMatch[3] = 0
            self.currMatch[2] = True
            self.currMatch[1] = 0
            self.currMatch[0] += 1
            # print("Fin iteration", self.currMatch[0])
        else:
            # print("Fin iteration", self.currMatch[0]+1)
            return
        self.start()

    def printQTable(self, i):
        """
        """
        print(self.playerStrats[i].name)
        for state, actions in self.playerQTables[i].items():
            print(state, actions)

    def printQTableDebug(self, i):
        """
        """
        print(self.count)
        print(self.playerStrats[i].name, len(self.playerQTables[i]))
        for state, actions in self.playerQTables[i].items():
            if np.amax(actions) > 1.:
                print(state, actions)
            elif np.amin(actions) < -1.:
                print(state, actions)

    def printAllQTables(self):
        """
        """
        print(self.name)
        for i in range(self.numPlayers):
            self.printQTable(i)
            print("===========================================")

    def save(self, filenames=[None]*4):
        """
        Sauvegarde la table Q(S,A) d'apprentissage de chaque joueur
        dans des fichiers dans le repertoire 'parameters'
        """
        for i in range(len(filenames)):
            if filenames[i] is None: continue
            with open(savePath(filenames[i]), "wb") as f:
                pickle.dump(self.playerQTables[i], f, protocol=pickle.HIGHEST_PROTOCOL)
