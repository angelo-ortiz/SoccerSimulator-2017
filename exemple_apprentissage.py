from soccersimulator import SoccerTeam, Simulation, show_simu,KeyboardStrategy,DTreeStrategy,load_jsonz,dump_jsonz
from soccersimulator import apprend_arbre, build_apprentissage, genere_dot
from ia.strategies_dectree import *
from ia.tools import StateFoot
import ia
import module
import sklearn
import numpy as np
import pickle

assert sklearn.__version__ >= "0.18.1","Updater sklearn !! (pip install -U sklearn --user )"



### Transformation d'un etat en features : state,idt,idp -> R^d

def my_get_features(state,idt,idp):
    """ extraction du vecteur de features d'un etat, ici distance a la balle, distance au but, distance balle but """
    state = StateFoot(state,idt,idp)#TODO a faire
    f1 = state.distance(state.ball_pos)
    f2 = state.distance(state.my_goal)
    f3 = state.distance_ball(state.my_goal)
    return [f1,f2,f3]

my_get_features.names = ["dball","dbut","dballbut"]


def entrainer(fname):
    #Creation d'une partie
    kb_strat = KeyboardStrategy()
    kb_strat.add("r",GoToMyGoalStrategy())#revenir
    kb_strat.add("m",PushUpStrategy())#monter
    kb_strat.add("s",PassStrategy())#faire passe
    kb_strat.add("k",ReceivePassStrategy())#recevoir passe
    kb_strat.add("q",CutDownAngleStrategy())#reduir angle
    kb_strat.add("l",MarkStrategy())#degager
    kb_strat.add("d",DribbleShootStrategy(fn_st="st_dico_FS7_2.pkl"))#frapper
    kb_strat.add("e",ControlDribbleStrategy(fn_st="st_dico_FS7_2.pkl"))#frapper
    
    team1 = SoccerTeam(name="Contol Team")
    team2 = module.get_team(2)
    team1.add("ControlPlayer",kb_strat) 
    team1.add("     ST",AttaquantStrategy(fn_st="st_dico_FS7_2.pkl")) 
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

    dic_strategy = {GoToMyGoalStrategy().name:GoToMyGoalStrategy(),
                    PushUpStrategy().name:PushUpStrategy(),
                    PassStrategy().name:PassStrategy(),
                    ReceivePassStrategy().name:ReceivePassStrategy(),
                    CutDownAngleStrategy().name:CutDownAngleStrategy(),
                    MarkStrategy().name:MarkStrategy(),
                    DribbleShootStrategy(fn_st="st_dico_FS7_2.pkl").name:DribbleShootStrategy(fn_st="st_dico_TME8.pkl"),
                    ControlDribbleStrategy(fn_st="st_dico_FS7_2.pkl").name:ControlDribbleStrategy(fn_st="st_dico_TME8.pkl")
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
    treeteam.add("    ST",AttaquantStrategy(fn_st="st_dico_FS7_2.pkl"))
    simu = Simulation(treeteam,team2)
    show_simu(simu)

