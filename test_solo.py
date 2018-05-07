from soccersimulator import SoccerAction,Vector2D,settings ,SoccerTeam,Billard,show_simu,Strategy
from ia.tools import StateFoot, get_empty_strategy
from ia.conditions import is_close_ball
from ia.actions import tryInterception, shootBillard

class FonceurLent(Strategy):
    def __init__(self):
        super(FonceurLent,self).__init__("fonceur")
    def compute_strategy(self,state,idteam,idplayer):
        ball = state.ball
        me = state.player_state(1,0)
        oth = state.balls[0]
        shoot = (oth.position-ball.position)*100
        if (me.position.distance(ball.position)<(settings.BALL_RADIUS+settings.PLAYER_RADIUS)) and  me.vitesse.norm<0.5:
            return SoccerAction(shoot=shoot)
        acc = ball.position-me.position
        if acc.norm<5:
            acc.norm=0.1
        return SoccerAction(acceleration=acc)

class BillardV1(Strategy):
    def __init__(self):
        super(BillardV1,self).__init__("billardV1")
        self.dico = dict()
        self.dico['tempsI'] = 120
        self.dico['n'] = -1
    def compute_strategy(self, state, idteam, idplayer):
        me = StateFoot(state, idteam, idplayer, 1)
        ball = state.ball
        # me = state.player_state(1,0)
        oth = state.balls[0]
        shoot = (oth.position-ball.position)*100
        ind = me.nextBall
        if ind == True:
            return get_empty_strategy()
        if is_close_ball(me, me.my_pos):
            #return SoccerAction(shoot=shoot)
            return shootBillard(me, ind, 2.)
        return tryInterception(me, self.dico)

# myt = SoccerTeam("prof")
# myt.add("N",FonceurLent())
myt = SoccerTeam("prof")
myt.add("N",BillardV1())
b = Billard(myt,type_game=2)
show_simu(b)

