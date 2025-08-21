import pytest
import sys
import os
from typing import List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/')))

from core import OtherEvent, EventBlock, Category, Team, MatchEvent
from utils.scheduler.scheduler import create_schedule
from model.model import Model

def test_create_schedule_other_events():
    test_model = Model()

    # Set days in model
    days = [0, 1, 2]
    test_model.set_days(days)
    
    # Add categories to model
    cats = []
    for i in range(5):
        if i % 3 == 0:
            group = 1
        elif i % 3 == 1:
            group = 2
        else:
            group = 3
        cats.append(Category("", str(group), 1, []))
    test_model.set_categories(cats)
        
    # Set after_events in model
    test_events = {}
    test_events["1"] = [
        OtherEvent(15, "", False, "", 0, "after", None),
        OtherEvent(10, "", False, "", 2, "after", None)]
    test_model.set_other_events(test_events)
    
    result = create_schedule(test_model)
    
    # Test number of days and blocks in tournament
    assert len(result) == 3
    for day in result:
        assert len(day.blocks) == 4
        for block in day.blocks:
            assert isinstance(block, EventBlock)
            
    # Test number of after_events
    for idx, day in enumerate(result):
        if idx == 1:
            assert day.blocks[1].number_of_events() == 2   # day 2 must have 2 events in 2nd block
        else:
            assert day.blocks[1].number_of_events() == 1   # all other days must have 1 event in 2nd block

    # Set before_events in model
    test_events = {}
    test_events["1"] = [
        OtherEvent(15, "", False, "", 0, "before", None),
        OtherEvent(10, "", False, "", 2, "before", None)]
    test_model.set_other_events(test_events)
    result = create_schedule(test_model)

    # Test number of before_events
    for idx, day in enumerate(result):
        if idx == 1:
            assert day.blocks[0].number_of_events() == 2   # day 2 must have 2 events in 1st block
        else:
            assert day.blocks[0].number_of_events() == 1   # all other days must have 1 event in 1st block

    # Set during_events in model
    test_events = {}
    test_events["3"] = [
        OtherEvent(15, "", False, "", 0, "during", 4),
        OtherEvent(10, "", False, "", 2, "during", 4)]
    test_model.set_other_events(test_events)
    result = create_schedule(test_model)

    # Test number of during_events
    for idx, day in enumerate(result):
        if idx == 1:
            assert day.blocks[2].number_of_events() == 2
        else:
            assert day.blocks[2].number_of_events() == 1

def test_create_schedule_one_category():
    test_model = Model()

    # Set days in model
    days = [0, 1, 2, 3, 4]
    test_model.set_days(days)

    # Set categories in model
    cats = []
    cats.append(Category("Open", "1", 2, _create_n_teams(11)))
    cats.append(Category("Foo", "2", 1, _create_n_teams(12)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    for i in range (1, 3):
        group_info[f"{i}"] = {
            "match_dur": 15,
            "num_fields": 2
        }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    for day in tournament:
        assert day.blocks[0].number_of_events() == 11
    
    event_counter = 0
    for idx, day in enumerate(tournament):
        event_counter += day.blocks[1].number_of_events()
        if idx <= 2:
            assert day.blocks[1].number_of_events() == 7
        else:
            assert day.blocks[1].number_of_events() == 6
    assert event_counter == 33

def test_create_schedule_two_categories():
    test_model = Model()

    # Set days in model
    days = [0, 1, 2, 3, 4]
    test_model.set_days(days)

    # Set categories in model
    cats = []
    cats.append(Category("U9", "1", 8, _create_n_teams(3)))
    cats.append(Category("U11", "2", 5, _create_n_teams(5)))
    cats.append(Category("U13", "1", 3, _create_n_teams(8)))
    cats.append(Category("U16", "2", 4, _create_n_teams(7)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    for i in range (1, 3):
        group_info[f"{i}"] = {
            "match_dur": 15,
            "num_fields": 2
        }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    for idx, day in enumerate(tournament):
        if idx == 0:
            assert day.blocks[0].number_of_matches() == 25
            assert day.blocks[0].number_of_events() == 13
        elif idx < 4:
            assert day.blocks[0].number_of_matches() == 21
            assert day.blocks[0].number_of_events() == 11
        elif idx == 4:
            assert day.blocks[0].number_of_matches() == 20
            assert day.blocks[0].number_of_events() == 10

    for idx, day in enumerate(tournament):
        if idx == 2 or idx == 3:
            assert day.blocks[1].number_of_events() == 13
            assert day.blocks[1].number_of_matches() == 25
        else:
            assert day.blocks[1].number_of_events() == 14
            assert day.blocks[1].number_of_matches() == 28

# Combine scheduling of OtherEvents and MatchEvents.
# Check if appending of MatchEvents starts at shortest day.
def test_create_schedule():
    test_model = Model()

    # Set days in model
    days = [i for i in range(5)]
    test_model.set_days(days)

    # Set events in model
    test_events = {}
    test_events["0"] = [
        OtherEvent(15, "Rangverkündigung", False, "", 5, "after", None)
        ]
    test_events["1"] = [
        OtherEvent(15, "Rangverkündigung", False, "", 5, "after", None)
        ]
    test_model.set_other_events(test_events)

    # Set categories in model
    cats = []
    cats.append(Category("U9", "1", 8, _create_n_teams(3)))
    cats.append(Category("U11", "2", 5, _create_n_teams(5)))
    cats.append(Category("U13", "1", 3, _create_n_teams(8)))
    cats.append(Category("U16", "2", 4, _create_n_teams(7)))
    cats.append(Category("Open", "3", 2, _create_n_teams(11)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    for i in range (1, 4):
        group_info[f"{i}"] = {
            "match_dur": 15,
            "num_fields": 2
        }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    match_counter_0 = match_counter_1 = match_counter_2 = 0

    for idx, day in enumerate(tournament):
        match_counter_0 += day.blocks[0].number_of_matches()
        match_counter_1 += day.blocks[1].number_of_matches()
        match_counter_2 += day.blocks[2].number_of_matches()
    assert match_counter_0 == 108
    assert match_counter_1 == 134
    assert match_counter_2 == 110

    for idx, day in enumerate(tournament):
        if idx == 0:
            assert day.total_duration() == 555
        elif idx == 1:
            assert day.total_duration() == 540
        else:
            assert day.total_duration() == 540

def test_create_schedule_different_rr_per_day():
    test_model = Model()

    # Set days in model
    days = [i for i in range(5)]
    test_model.set_days(days)

    # Set events in model
    test_events = {}
    test_events["0"] = [
        OtherEvent(15, "Rangverkündigung", False, "", 5, "after", None)
        ]
    test_model.set_other_events(test_events)

    # Set categories in model
    cats = []
    cats.append(Category("Cat1", "1", 4, _create_n_teams(5)))
    cats.append(Category("Cat2", "1", 4, _create_n_teams(7)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    group_info[f"{1}"] = {
        "match_dur": 15,
        "num_fields": 2
    }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    assert tournament[0].blocks[0].number_of_matches() == 26
    assert tournament[1].blocks[0].number_of_matches() == 26
    assert tournament[2].blocks[0].number_of_matches() == 26
    assert tournament[3].blocks[0].number_of_matches() == 23
    assert tournament[4].blocks[0].number_of_matches() == 23



def test_double_mission_handling_pause():
    test_model = Model()

    # Set days in model
    days = [i for i in range(5)]
    test_model.set_days(days)

    # Set events in model
    test_events = {}
    test_events["1"] = [
        OtherEvent(15, "", False, "", 1, "during", 2)
        ]
    test_model.set_other_events(test_events)

    # Set categories in model
    cats = []
    cats.append(Category("Cat1", "1", 4, _create_n_teams(5)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    group_info[f"{1}"] = {
        "match_dur": 15,
        "num_fields": 2,
        "double_missions": "pause",
        "pause_dur": 5
    }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    for day in tournament:
        assert day.blocks[0].number_of_matches() == 8
    
    assert tournament[0].total_duration() == 85
    assert tournament[1].total_duration() == 75
    assert tournament[4].total_duration() == 75
    assert tournament[0].blocks[0].number_of_events() == 7

def test_double_mission_handling_empty_field():
    test_model = Model()

    # Set days in model
    days = [i for i in range(5)]
    test_model.set_days(days)

    # Set events in model
    test_events = {}
    test_events["1"] = [
        OtherEvent(15, "", False, "", 1, "during", 2)
        ]
    test_model.set_other_events(test_events)

    # Set categories in model
    cats = []
    cats.append(Category("Cat1", "1", 4, _create_n_teams(6)))
    test_model.set_categories(cats)

    # Set grouping infos in model
    group_info = {}
    group_info[f"{1}"] = {
        "match_dur": 15,
        "num_fields": 2,
        "double_missions": "empty_field"
    }
    test_model.set_group_info(group_info)
    
    tournament = create_schedule(test_model)

    assert tournament[0].blocks[0].total_duration() == 150
    assert tournament[1].blocks[0].total_duration() == 135
    assert tournament[2].blocks[0].total_duration() == 135
    assert tournament[3].blocks[0].total_duration() == 135
    assert tournament[4].blocks[0].total_duration() == 135

    assert len(tournament[0].blocks[0].get_event(1).matches) == 1
    assert len(tournament[0].blocks[0].get_event(4).matches) == 1
    assert len(tournament[0].blocks[0].get_event(5).matches) == 1
    assert len(tournament[0].blocks[0].get_event(7).matches) == 0
    assert len(tournament[0].blocks[0].get_event(9).matches) == 1

    assert len(tournament[1].blocks[0].get_event(4).matches) == 0
    

def _create_n_teams(num_teams: int) -> list:
    teams = []
    for i in range(num_teams):
        teams.append(Team(f"team{i}", "", None))
    return teams
