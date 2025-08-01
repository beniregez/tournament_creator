from model.model import Model
# from rr_run import create_n_rr_runs
from core import EventBlock

def create_schedule(model: Model):
    num_days = len(model.get_days())

    # 1. Create empty days
    tournament = [[] for _ in range(num_days)]

    # 2. Create empty EventBlocks. We need n + 1 because after last grouping block there might be after_events
    # which must be added to a dedicated EventBlock.
    num_blocks = len(model.get_unique_groups()) + 1
    for day in tournament:
        for i in range(num_blocks):
            day.append(EventBlock())

    # 3. Fill in OtherEvents
    other_events = model.get_other_events()
    
    # 3.a Append after-events at begin of next group block
    for group, group_events in other_events.items():
        group_idx = int(group) # We append with after_events, therefore append at next block. "-1" not needed.
        for e in group_events:
            if e.bef_dur_aft == "after":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day[group_idx].add_event(e)
                else:
                    tournament[e.day_index - 1][group_idx].add_event(e)
            
    # 3.b Add before-events at begin of current group block
    for group, group_events in other_events.items():
        group_idx = int(group) - 1
        for e in group_events:
            if e.bef_dur_aft == "before":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day[group_idx].add_event(e)
                else:
                    tournament[e.day_index - 1][group_idx].add_event(e)
    
    # 3.c Add during-events at correct index (with respect to before-events)
    for group, group_events in other_events.items():
        group_idx = int(group) - 1
        for e in group_events:
            if e.bef_dur_aft == "during":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day[group_idx].add_event_after_n_nones(e.dur_index, e)
                else:
                    tournament[e.day_index - 1][group_idx].add_event_after_n_nones(e.dur_index, e)
    

    # TODO 4. Fill with MatchEvents
    
    # TODO 5. 'Flatten' Day (create 1 event list per day)

    return tournament
