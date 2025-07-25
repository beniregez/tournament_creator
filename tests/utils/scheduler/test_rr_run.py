import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/')))

from core import Team, Match, Category
from utils.scheduler.rr_run import create_rr_run, create_n_rr_runs


def test_create_rr_run():
    teams = []
    for i in range(0,5):
        teams.append(Team(str(i), "#FFFFFF", None))
    cat = Category("", "", 0, teams)
    result = create_rr_run(cat)
    
    assert isinstance(result, list)
    assert len(result) == 5
    for row in result:
        for m in row:
            assert isinstance(m, Match)
        assert len(row) == 2
    
    cat.teams.append(Team("5", "#FFFFFF", None))
    result2 = create_rr_run(cat)
    assert isinstance(result2, list)
    assert len(result2) == 5
    for row in result2:
        for m in row:
            assert isinstance(m, Match)
        assert len(row) == 3
        
def test_create_n_rr_runs():
    teams = []
    for i in range(0,5):
        teams.append(Team(str(i), "#FFFFFF", None))
    cat = Category("", "", 2, teams)

    result = create_n_rr_runs(cat)
    assert isinstance(result, list)
    
    assert result[0][0].team1 == result[5][0].team2
    
    assert len(result) == 10