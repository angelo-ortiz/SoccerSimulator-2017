from soccersimulator import SoccerTeam, Simulation, show_simu, KeyboardStrategy, \
    DTreeStrategy, load_jsonz, dump_jsonz
from soccersimulator import apprend_arbre, build_apprentissage, genere_dot
from ia.tools import *
from ia.strategies import Attaquant2v2Strategy, Gardien2v2Strategy
from ia.dt_strategies import *
import ia
import module
import module6
import sklearn
import numpy as np
import pickle
from math import acos

assert sklearn.__version__ >= "0.18.1","Updater sklearn !! (pip install -U sklearn --user )"



### Transformation d'un etat en features : state,idt,idp -> R^d

def my_get_features(state,idt,idp):
    """ extraction du vecteur de features d'un etat, ici distance a la balle, distance au but, distance balle but """
    me = StateFoot(state,idt,idp)#TODO a faire

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


def entrainer(fname):
    #Creation d'une partie
    kb_strat = KeyboardStrategy()
    #kb_strat.add("z",GoToMyGoalStrategy())#revenir
    kb_strat.add("z",Gardien2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))#defendre
    #kb_strat.add("m",PushUpStrategy())#monter
    #kb_strat.add("s",PassStrategy())#faire passe
    kb_strat.add("q",PassiveSituationStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))#recevoir passe
    #kb_strat.add("k",CutDownAngleStrategy())#reduire angle
    #kb_strat.add("l",MarkStrategy())#degager
    kb_strat.add("d",DribbleShootStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))#frapper
    kb_strat.add("s",ControlDribbleStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))#avancer

    # TODO utiliser une boucle
    # changer de cote et ajouter d'autres equipes nota° module6
    team1 = SoccerTeam(name="Contol Team")
    team2 = module.get_team(2)
    team1.add("ControlPlayer",kb_strat) 
    team1.add("     ST",Attaquant2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl")) 
    simu = Simulation(team1,team2,max_steps=4000)
    #Jouer, afficher et controler la partie
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

    entrainer("test_kb_strat.jz")

    dic_strategy = {Gardien2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl").name:Gardien2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"), \
                    PassiveSituationStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl").name:PassiveSituationStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"),
                    DribbleShootStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl").name:DribbleShootStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"),
                    ControlDribbleStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl").name:ControlDribbleStrategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl")
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
    treeteam.add("    ST",Attaquant2v2Strategy(fn_gk="gk_dico_0325_p5_short.pkl", fn_st="st_dico_0325_p5_short.pkl"))
    simu = Simulation(treeteam,team2)
    show_simu(simu)

