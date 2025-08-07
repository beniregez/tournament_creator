from model.model import Model
from .rr_run import create_n_rr_runs
from core import EventBlock, Category, Team, Match, MatchEvent

def create_schedule(model: Model):
    num_days = len(model.get_days())

    # 1. Create empty days
    tournament = [[] for _ in range(num_days)]

    # 2. Create empty EventBlocks. We need n + 1 because after last grouping block there might be after_events
    # which must be added to a dedicated EventBlock.
    num_blocks = len(model.get_unique_groups()) + 1
    for day in tournament:
        for _ in range(num_blocks):
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
    
    # 4. Create rr_runs for every category
    categories = model.get_categories()
    rr_runs = []
    for cat in categories:
        rr_runs.append(create_n_rr_runs(cat, True))

    # TODO 5. Merge and distribute runs / matches of categories in same group on EventBlocks (starting at the shortest day)
    group_info = model.get_group_info()
    for group_idx, group in enumerate(group_info):
        # collect category indices in the current group
        cat_indices = []
        for cat_idx, cat in enumerate(categories):
            if cat.group == group:
                cat_indices.append(cat_idx)

        curr_group_info = group_info[group]
        match_dur = curr_group_info["match_dur"]
        num_fields = curr_group_info["num_fields"]

        # Case 1: One single category in group
        # TODO: Check for double missions and apply wished strategy:
        # (a) empty fields, (b) break, (c) indifference
        if len(cat_indices) == 1:
            cat_idx = cat_indices[0]

            flattened_matches = flatten_2d_list(rr_runs[cat_idx])   # Matches as a 1D-list
            num_matches = len(flattened_matches)
            num_match_events = num_matches // num_fields
            num_remain_matches =  num_matches - (num_match_events * num_fields)

            match_events_per_day = num_match_events // num_days
            num_remain_match_events = num_match_events - (match_events_per_day * num_days)

            match_idx = 0

            for day_idx in range(num_days):
                for m_e in range(match_events_per_day):
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_fields):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    tournament[day_idx][group_idx].add_event_to_next_available_slot(curr_event)
                # (i) EITHER append an entire additional match_event (if remaining)
                if num_remain_match_events > 0:
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_fields):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    num_remain_match_events -= 1
                    tournament[day_idx][group_idx].add_event_to_next_available_slot(curr_event)
                # (ii) OR append a partial match_event (if remaining)
                elif num_remain_matches > 0:
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_remain_matches):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    tournament[day_idx][group_idx].add_event_to_next_available_slot(curr_event)
                    num_remain_matches = 0  # No remaining matches that do not fill an entire match event

        # Case 2: Two or more categories in group
        elif len(cat_indices) > 1:
            pass

    # TODO: flatten all blocks (remove nones).
    return tournament

def flatten_2d_list(rr_runs: list) -> list:
    matches = []
    for rr in rr_runs:
        for match in rr:
            matches.append(match)
    return matches
