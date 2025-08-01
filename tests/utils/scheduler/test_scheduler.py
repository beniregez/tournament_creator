import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/')))

from core import OtherEvent, EventBlock, Category
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
        cats.append(Category("", str(group), "1", []))
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
        assert len(day) == 4
        for e in day:
            assert isinstance(e, EventBlock)
            
    # Test number of after_events
    for idx, day in enumerate(result):
        if idx == 1:
            assert day[1].number_of_events() == 2   # day 2 must have 2 events in 2nd block
        else:
            assert day[1].number_of_events() == 1   # all other days must have 1 event in 2nd block

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
            assert day[0].number_of_events() == 2   # day 2 must have 2 events in 1st block
        else:
            assert day[0].number_of_events() == 1   # all other days must have 1 event in 1st block

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
            assert day[2].number_of_events() == 2
            assert day[2].get_event(4).duration == 15
            assert day[2].get_event(5).duration == 10
        else:
            assert day[2].number_of_events() == 1
            assert day[2].get_event(4).duration == 15