import copy
from core import Team, Match, Category

def create_rr_run(cat: Category):
    teams = copy.copy(cat.teams)
    if len(teams) % 2 == 1:
        teams.append(None) # If odd number: Append with a "dummy" team
        
    rr_run = []
    n = len(teams)

    for rr in range(n - 1):
        rr_matches = []
        
        for i in range(n // 2):
            team1 = teams[i]
            team2 = teams[n - 1 - i]
            if team1 is not None and team2 is not None:
                rr_matches.append(Match(team1, team2))
        rr_run.append(rr_matches)

        # Rotate teams (without first team)
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    return rr_run