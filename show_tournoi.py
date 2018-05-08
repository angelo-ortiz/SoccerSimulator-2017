from soccersimulator import show_simu,load_jsonz
import sys

try:
    input = raw_input
except NameError:
    pass

if __name__=="__main__":
    if len(sys.argv)!=2:
        print("Usage : %s file.jz" % sys.argv[0])
        sys.exit(0)
    tournoi = load_jsonz(sys.argv[1])
    key =''
    while key !='q':
        tournoi.print_scores(True)
        key = input("Match ? : ")
        try:
            i,j = [int(x) for x in key.split(" ")]
            show_simu(tournoi.get_match(i,j))
        except:
            matches = tournoi.get_matches(int(key))
            for match in matches:
                print(match.get_score_team(1),match.get_score_team(2))
                print(match.team1.name, match.team2.name)
            key = 'q'
