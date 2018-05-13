from soccersimulator import SoccerTeam, Simulation, show_simu, KeyboardStrategy, \
    DTreeStrategy, load_jsonz, dump_jsonz
from soccersimulator import apprend_arbre, build_apprentissage, genere_dot
from ia.tools import *
from ia.strategies import Attaquant2v2Strategy, Gardien2v2Strategy
from ia.dt_strategies import *
import ia
import module
import module4
import module6
import sklearn
import numpy as np
import pickle
from math import acos

assert sklearn.__version__ >= "0.18.1","Updater sklearn !! (pip install -U sklearn --user )"

fn_gk = "2v2_gk_dico_0428_1.pkl"
fn_st = "2v2_st_dico_0428_1.pkl"

### Transformation d'un etat en features : state,idt,idp -> R^d

def my_get_features(state,idt,idp):
    """ extraction du vecteur de features d'un etat, ici distance a la balle, distance au but, distance balle but """
    me = StateFoot(state,idt,idp)

    dJB = me.distance(me.ball_pos) # distance entre le joueur et la balle
    dJmC = me.distance(me.my_goal) # distance entre le joueur et sa cage
    dJoC = me.distance(me.opp_goal) # distance entre le joueur et la cage adverse
    oppNearest = nearest(me.my_pos, me.opponents) # l'adversaire le plus proche du joueur
    dJDef = me.distance(oppNearest) # distance entre le joueur et l'adversaire le plus proche
    doNearoC = oppNearest.distance(me.opp_goal) # distance entre l'adversaire le plus proche du joueur et sa cage

    opp_goal_my_pos = (me.my_pos - me.opp_goal).normalize()
    opp_goal_my_goal = (me.my_goal - me.opp_goal).normalize()
    angleGoal = acos(opp_goal_my_pos.dot(opp_goal_my_goal)) # angle entre le joueur et la cage adverse
    
    dBmC = me.distance_ball(me.my_goal) # distance entre la balle et la cage du joueur
    dBoC = me.distance_ball(me.opp_goal) # distance entre la balle et la cage adverse au joueur
    
    tm = me.teammates[0] # coequipier du joueur
    oppNearestTM = nearest(tm.position, me.opponents) # l'adversaire le plus proche du coequipier
    dTMDef = tm.position.distance(oppNearestTM) # la distance entre le coequipier et son adversaire le plus proche
    dTMB = me.distance_ball(tm.position) # distance entre le coequipier et la balle
    dTMoC = tm.position.distance(me.opp_goal) # distance entre le coequipier et la cage adverse
    
    return [dJB, dJmC, dJmC, dJDef, doNearoC, angleGoal, dBmC, dBoC, dTMDef, dTMB, dTMoC]

my_get_features.names = ["dJB", "dJmC", "dJmC", "dJDef", "doNearoC", "angleGoal", "dBmC", "dBoC", "dTMDef", "dTMB", "dTMoC"]


def entrainer(fname,nbiter):
    #Creation d'une partie
    kb_strat = KeyboardStrategy()
    kb_strat.add("z",Gardien2v2Strategy(fn_gk=fn_gk, fn_st=fn_st))#defendre
    #kb_strat.add("m",PushUpStrategy())#monter
    #kb_strat.add("s",PassStrategy())#faire passe
    #kb_strat.add("q",PassiveSituationStrategy(fn_gk=fn_gk, fn_st=fn_st))#recevoir passe
    kb_strat.add("q",GoToMyGoalStrategy())#revenir
    #kb_strat.add("k",CutDownAngleStrategy())#reduire angle
    #kb_strat.add("l",MarkStrategy())#degager
    kb_strat.add("d",DribbleShootStrategy(fn_gk=fn_gk, fn_st=fn_st))#frapper
    kb_strat.add("s",ControlDribbleStrategy(fn_gk=fn_gk, fn_st=fn_st))#avancer

    team1 = SoccerTeam(name="Contol Team")
    oppList = [module.get_team(2), module4.get_team(2), module6.get_team(2)]
    team1.add("ControlPlayer",kb_strat) 
    team1.add("     ST",Attaquant2v2Strategy(fn_gk=fn_gk, fn_st=fn_st))
    for i in range(nbiter):
        for team2 in oppList:
            #Jouer, afficher et controler la partie
            simu = Simulation(team1,team2,max_steps=2000)
            show_simu(simu)
            simu = Simulation(team2,team1,max_steps=2000)
            show_simu(simu)
    print("Nombre d'exemples : "+str(len(kb_strat.states)))
    # Sauvegarde des etats dans un fichier
    dump_jsonz(kb_strat.states,fname)

def apprendre(exemples, get_features,fname=None):
    #genere l'ensemble d'apprentissage
    data_train, data_labels = build_apprentissage(exemples,get_features)
    ## Apprentissage de l'arbre
    dt = apprend_arbre(data_train,data_labels,depth=10,feature_names=get_features.names)
    ##Sauvegarde de l'arbre
    if fname is not None:
        with open(fname,"wb") as f:
            pickle.dump(dt,f)
    return dt

if __name__=="__main__":

    #entrainer("test_kb_strat.jz", 1)

    dic_strategy = {Gardien2v2Strategy().name:Gardien2v2Strategy(fn_gk=fn_gk, fn_st=fn_st), \
                    GoToMyGoalStrategy().name:GoToMyGoalStrategy(), \
                    DribbleShootStrategy().name:DribbleShootStrategy(fn_gk=fn_gk, fn_st=fn_st),\
                    ControlDribbleStrategy().name:ControlDribbleStrategy(fn_gk=fn_gk, fn_st=fn_st)
    }

    states_tuple = load_jsonz("test_kb_strat.jz")
    apprendre(states_tuple,my_get_features,"tree_test.pkl")
    with open("tree_test.pkl","rb") as f:
        dt = pickle.load(f)
    # Visualisation de l'arbre
    genere_dot(dt,"test_arbre.dot")
    #Utilisation de l'arbre : arbre de decision, dico strategy, fonction de transformation etat->variables
    treeStrat1 = DTreeStrategy(dt,dic_strategy,my_get_features)
    treeteam = SoccerTeam("Arbre Team")
    team2 = module.get_team(2)
    treeteam.add("    GK",treeStrat1)
    treeteam.add("    ST",Attaquant2v2Strategy(fn_gk=fn_gk, fn_st=fn_st))
    simu = Simulation(treeteam,team2)
    show_simu(simu)

