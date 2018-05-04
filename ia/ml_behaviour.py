# -*- coding: utf-8 -*-
from soccersimulator import SoccerAction, Vector2D
from soccersimulator.settings import maxPlayerShoot
from .tools import StateFoot, nearest_defender, get_empty_strategy, shootPower, \
    distance_horizontale
from .conditions import is_close_goal, free_teammate, has_ball_control, \
    free_opponent, both_must_kick
from .actions import kickAt, shoot, control, dribble, passBall, mark, loseMark, clear, \
    tryInterception, pushUp, goToBall, cutDownAngle, cutDownAngle_gk, cutDownAngle_def

def st_kick_off(state, dico):
    if has_ball_control(state):
        count = both_must_kick(state)
        if count > 1:
            return cutDownAngle_gk(state, 40.)
        if count == 1:
            return shoot(state, maxPlayerShoot)
        return control(state, dico['controleMT'])
    return goToBall(state)

def gk_kick_off(state, dico):
    if has_ball_control(state):
        count = both_must_kick(state)
        if count == 1:
            return kickAt(state, Vector2D(state.opp_goal.x, 100.), maxPlayerShoot)
        return cutDownAngle_gk(state, 40.)
    return goToBall(state)

def ml_mark(state, dico):
    oppAtt = free_opponent(state, 60., dico['rayPressing'])
    if oppAtt is not None:
        return mark(state, oppAtt, dico['rayPressing'])#20.
    return get_empty_strategy()

def ml_dribble(state, dico):
    oppDef = nearest_defender(state, state.opponents, dico['rayDribble'])
    if oppDef is not None:
        return dribble(state, oppDef, dico['angleDribble'], dico['powerDribble'], dico['coeffAD'])
    return control(state, dico['controleMT'])

def ml_pass(state, dico):
    tm = free_teammate(state, dico['angleInter'])
    if tm is not None:
        coeffPushUp = dico['coeffPushUp']
        if is_close_goal(state, dico['distShoot']):
            coeffPushUp /= 2.
        return passBall(state, tm, dico['powerPasse'], dico['thetaPasse'], coeffPushUp) + \
            pushUp(state, dico['coeffPushUp'])
    return control(state, dico['controleMT'])

def shoot_mark(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return ml_mark(state, dico)

def shoot_loseMark(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])

def shoot_intercept(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return tryInterception(state, dico)

def shoot_pushUp(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return pushUp(state, dico['coeffPushUp'])

def shoot_goToBall(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return goToBall(state)

def shoot_cutDownAngle_st(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])#60., 20.)

def dribble_mark(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return ml_mark(state, dico)

def dribble_loseMark(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])

def dribble_intercept(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return tryInterception(state, dico)

def dribble_pushUp(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return pushUp(state, dico['coeffPushUp'])

def dribblet_goToBall(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return goToBall(state)

def dribble_cutDownAngle_st(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])#60., 20.)

def control_mark(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return ml_mark(state, dico)

def control_loseMark(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])

def control_intercept(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return tryInterception(state, dico)

def control_pushUp(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return pushUp(state, dico['coeffPushUp'])

def control_goToBall(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return goToBall(state)

def control_cutDownAngle_st(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])#60., 20.)

def pass_mark(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return ml_mark(state, dico)

def pass_loseMark(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])

def pass_intercept(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return tryInterception(state, dico)

def pass_pushUp(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return pushUp(state, dico['coeffPushUp'])

def pass_goToBall(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return goToBall(state)

def pass_cutDownAngle_st(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])#60., 20.)

def clear_mark(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

def clear_loseMark(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return loseMark(state, dico['rayPressing'], dico['distDemar'], dico['angleInter'])

def clear_intercept(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return tryInterception(state, dico)

def clear_pushUp(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return pushUp(state, dico['coeffPushUp'])

def clear_goToBall(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return goToBall(state)

def clear_cutDownAngle_st(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return cutDownAngle(state, dico['raySortie'], dico['rayInter'])#60., 20.)

def shoot_cutDownAngle_gk(state, dico):
    if has_ball_control(state):
        return shoot(state, shootPower(state, dico['alphaShoot'], dico['betaShoot']))
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

def dribble_cutDownAngle_gk(state, dico):
    if has_ball_control(state):
        return ml_dribble(state, dico)
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

def control_cutDownAngle_gk(state, dico):
    if has_ball_control(state):
        return control(state, dico['controleMT'])
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

def pass_cutDownAngle_gk(state, dico):
    if has_ball_control(state):
        return ml_pass(state, dico)
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

def clear_cutDownAngle_gk(state, dico):
    if has_ball_control(state):
        return clear(state, angleClear=1.2)
    return cutDownAngle_def(state, dico['distMontee']+10., dico['rayInter'])#60., 20.)

attDict = {
    5: shoot_mark,
    1: shoot_loseMark,
    2: shoot_intercept,
    3: shoot_pushUp,
    4: shoot_goToBall,
    0: shoot_cutDownAngle_st,
    6: dribble_mark,
    7: dribble_loseMark,
    8: dribble_intercept,
    9: dribble_pushUp,
    10: dribblet_goToBall,
    11: dribble_cutDownAngle_st,
    12: control_mark,
    13: control_loseMark,
    14: control_intercept,
    15: control_pushUp,
    16: control_goToBall,
    17: control_cutDownAngle_st,
    18: pass_mark,
    19: pass_loseMark,
    20: pass_intercept,
    21: pass_pushUp,
    22: pass_goToBall,
    23: pass_cutDownAngle_st,
    24: clear_mark,
    25: clear_loseMark,
    26: clear_intercept,
    27: clear_pushUp,
    28: clear_goToBall,
    29: clear_cutDownAngle_st
}

defDictUpdate = {
    0: shoot_cutDownAngle_gk,
    11: dribble_cutDownAngle_gk,
    17: control_cutDownAngle_gk,
    23: pass_cutDownAngle_gk,
    29: clear_cutDownAngle_gk
}

defDict = attDict.copy()
for k,v in defDictUpdate.items():
    defDict[k] = v
