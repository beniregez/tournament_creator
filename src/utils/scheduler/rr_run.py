import copy
from core import Team, Match, Category

def create_rr_run(cat: Category, alter_home_away: bool = False):
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
                if alter_home_away:
                    rr_matches.append(Match(team2, team1))
                else:
                    rr_matches.append(Match(team1, team2))
        rr_run.append(rr_matches)

        # Rotate teams (without first team) for next round robin
        teams = [teams[0]] + [teams[-1]] + teams[1:-1]
    return rr_run

def create_n_rr_runs(cat: Category, alter_home_away: bool = True):
    rr_runs = []
    
    if alter_home_away:
        for run_idx in range(int(cat.runs)):
            if run_idx % 2 == 0:
                rr_run = create_rr_run(cat, False)
            else:
                rr_run = create_rr_run(cat, True)
            rr_runs.extend(rr_run)  # Add all rounds one after another
    else:
        for run_idx in range(cat.runs):
            rr_runs.extend(create_rr_run(cat, False))   # Add all rounds one after another
    
    return rr_runs