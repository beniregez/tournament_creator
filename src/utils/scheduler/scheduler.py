import math
from typing import List

from model.model import Model
from .rr_run import create_n_rr_runs
from core import EventDay, EventBlock, Category, Team, Match, MatchEvent

def create_schedule(model: Model) -> List[EventDay]:
    num_days = len(model.get_days())

    # 1. Create empty EventDays
    # tournament = [[] for _ in range(num_days)]
    tournament = [EventDay() for _ in range(num_days)]

    # 2. Create empty EventBlocks. We need n + 1 because after last grouping block there might be after_events
    # which must be added to a dedicated EventBlock.
    num_blocks = len(model.get_unique_groups()) + 1
    for day in tournament:
        for _ in range(num_blocks):
            day.blocks.append(EventBlock())

    # 3. Fill in OtherEvents
    other_events = model.get_other_events()
    
    # 3.a Append after-events at begin of next group block
    for group, group_events in other_events.items():
        group_idx = int(group) # We append with after_events, therefore append at next block. "-1" not needed.
        for e in group_events:
            if e.bef_dur_aft == "after":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day.blocks[group_idx].add_event(e)
                else:
                    tournament[e.day_index - 1].blocks[group_idx].add_event(e)
            
    # 3.b Add before-events at begin of current group block
    for group, group_events in other_events.items():
        group_idx = int(group) - 1
        for e in group_events:
            if e.bef_dur_aft == "before":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day.blocks[group_idx].add_event(e)
                else:
                    tournament[e.day_index - 1].blocks[group_idx].add_event(e)
    
    # 3.c Add during-events at correct index (with respect to before-events)
    for group, group_events in other_events.items():
        group_idx = int(group) - 1
        for e in group_events:
            if e.bef_dur_aft == "during":
                if e.day_index == 0: # event takes place at all days
                    for day in tournament:
                        day.blocks[group_idx].add_event_after_n_nones(e.dur_index, e)
                else:
                    tournament[e.day_index - 1].blocks[group_idx].add_event_after_n_nones(e.dur_index, e)
    
    # 4. Create rr_runs for every category
    categories = model.get_categories().copy()
    rr_runs = []
    for cat in categories:
        rr_list = create_n_rr_runs(cat, True)
        rr_runs.append(rr_list)
        cat.rr_runs = rr_list
        cat.matches = flatten_2d_list(rr_list)
        # Add metrics to category
        cat.num_matches_per_rr = len(cat.teams) // 2
        cat.num_rr_per_day = len(rr_list) / num_days
        cat.num_rr_per_day_floored = math.floor(cat.num_rr_per_day)
        cat.num_rr_remaining = len(cat.rr_runs) - (num_days * cat.num_rr_per_day_floored)

    # 5. Merge and distribute runs / matches of categories in same group on EventBlocks (starting at the shortest day)
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

        shortest_day_idx = get_shortest_day_idx(tournament)

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
                mod_day_idx = get_modified_day_idx(day_idx, shortest_day_idx, num_days)
                for m_e in range(match_events_per_day):
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_fields):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    tournament[mod_day_idx].blocks[group_idx].add_event_to_next_available_slot(curr_event)
                # (i) EITHER append an entire additional match_event (if remaining)
                if num_remain_match_events > 0:
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_fields):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    num_remain_match_events -= 1
                    tournament[mod_day_idx].blocks[group_idx].add_event_to_next_available_slot(curr_event)
                # (ii) OR append a partial match_event (if remaining)
                elif num_remain_matches > 0:
                    curr_event = MatchEvent(match_dur, [])
                    for m in range(num_remain_matches):
                        curr_event.matches.append(flattened_matches[match_idx])
                        match_idx += 1
                    tournament[mod_day_idx].blocks[group_idx].add_event_to_next_available_slot(curr_event)
                    num_remain_matches = 0  # No remaining matches that do not fill an entire match event

        elif len(cat_indices) > 1:
            group_cats = [categories[c] for c in cat_indices]
            group_cats_sorted = sorted(group_cats, key=lambda cat: cat.num_rr_per_day, reverse=True) # Sort by rr_per_day in ascending order

            num_rr_per_cat_and_day = [[] for _ in range(num_days)]
            # Compute number of categories rr for each day
            for cat_idx, cat in enumerate(group_cats_sorted):
                for d_idx, d in enumerate(num_rr_per_cat_and_day):
                    if d_idx < cat.num_rr_remaining:    # If remainder: append another rr
                        d.append(cat.num_rr_per_day_floored + 1)
                    else:
                        d.append(cat.num_rr_per_day_floored)

            matches_per_day = [[] for _ in range(num_days)] # List of list of Matches
            match_indices = [0 for _ in range(len(group_cats_sorted))]

            for day_idx in range(len(num_rr_per_cat_and_day)):
                num_rr_per_cat = num_rr_per_cat_and_day[day_idx]

                num_rounds = max(num_rr_per_cat) # Number of rounds depends on longest category
                rounds = [[] for _ in range(num_rounds)]    # List of Matches

                # Distribute category matches on rounds
                for cat_idx, cat in enumerate(group_cats_sorted):
                    cat_num_rr = num_rr_per_cat[cat_idx]
                    # Case 1 (num_rr is similar): Append entire rr per round
                    if num_rounds <= (cat_num_rr + 1):
                        for round_idx in range(cat_num_rr):
                            for _ in range(cat.num_matches_per_rr):
                                rounds[round_idx].append(cat.matches[match_indices[cat_idx]])
                                match_indices[cat_idx] += 1
                    # Case 2 (num_rr is different): Fill gaps with (partial) rr
                    else:
                        num_gaps = num_rounds - 1 if num_rounds - 1 > 0 else 1
                        gaps = [0 for _ in range(num_gaps)]

                        gaps_per_rr = num_gaps // cat_num_rr
                        gaps_remainder = num_gaps % cat_num_rr

                        rr_splits_to_gaps = [gaps_per_rr for _ in range(cat_num_rr)]
                        for x in range(gaps_remainder):
                            rr_splits_to_gaps[x] += 1
                        rr_splits_to_gaps.reverse()

                        m_per_gap = []
                        for split in rr_splits_to_gaps:
                            gaps = [0 for _ in range(split)]
                            for m_idx in range(cat.num_matches_per_rr):
                                gaps[(m_idx % split)] += 1
                            m_per_gap.extend(gaps)
                        
                        # If last gap round is shorter than first: reverse m_per_gap
                        if num_rounds > 1:
                            if len(rounds[-2]) < len(rounds[0]):
                                m_per_gap.reverse()

                        # Append matches to rounds according to m_per_gap
                        for gap_idx, num_matches in enumerate(m_per_gap):
                            for match_idx in range(num_matches):
                                rounds[gap_idx].append(cat.matches[match_indices[cat_idx]])
                                match_indices[cat_idx] += 1

                # Append all matches to days list
                for round in rounds:
                    matches_per_day[day_idx].extend(round)
                
            # Append matches_per_day to tournament.
            for day_idx in range(num_days):
                mod_day_idx = get_modified_day_idx(day_idx, shortest_day_idx, num_days)
                curr_event = MatchEvent(match_dur, [])
                for m in matches_per_day[day_idx]:
                    curr_event.matches.append(m)
                    if (len(curr_event.matches) == num_fields):
                        tournament[mod_day_idx].blocks[group_idx].add_event_to_next_available_slot(curr_event)
                        curr_event = MatchEvent(match_dur, [])
                    # If there remains a partial MatchEvent: Append it to the tournament too
                if len(curr_event.matches) > 0:
                    tournament[mod_day_idx].blocks[group_idx].add_event_to_next_available_slot(curr_event)

    # 6. Compact all blocks (remove nones).
    for day_idx in tournament:
        for block in day_idx.blocks:
            block.events = block.get_valid_events()
    return tournament

def flatten_2d_list(rr_runs: list) -> list:
    matches = []
    for rr in rr_runs:
        for match in rr:
            matches.append(match)
    return matches

def get_shortest_day_idx(tournament: List[EventDay]) -> int:
    day_idx = 0
    day_dur = tournament[0].total_duration()
    for d_idx, d in enumerate(tournament):
        curr_dur = d.total_duration()
        if curr_dur < day_dur:
            day_idx = d_idx
            day_dur = curr_dur
    return day_idx

def get_modified_day_idx(day_idx: int, shortest_day_idx: int, num_days: int) -> int:
    return (day_idx + shortest_day_idx) % num_days