import copy
import hashlib
import math
import random
from typing import List

from model.model import Model
from .rr_run import create_n_rr_runs
from core import EventDay, EventBlock, Category, Team, Match, MatchEvent, OtherEvent

def create_schedule(model: Model) -> List[EventDay]:
    num_days = len(model.get_days())
    if num_days == 0:
        return []

    # 1. Create empty EventDays
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
    categories = copy.deepcopy(model.get_categories())
    if model.get_tournament_info().get("shuffle", False):   # Shuffle team order if set to True
        shuffle_seed = model.get_tournament_info().get("shuffle_seed", 0)
        print(f"Scheduling with shuffle_seed: '{shuffle_seed}'")
        for cat in categories:
            cat.teams = shuffle_with_seed(cat.teams, shuffle_seed)
    else:
        print("Scheduling without shuffling.")
    rr_runs = []
    for cat in categories:
        rr_list = create_n_rr_runs(cat, True)

        # Prevent identical consecutive day schedule for a category
        if model.get_tournament_info().get("prevent_identical_cat_days", False):
            if int(cat.runs) % num_days == 0:
                day_length = len(rr_list) // num_days
                # Let first
                rotated = rr_list[:day_length]
                new_rr_list = rotated.copy()
                # From day 2 on: Rotate and append
                for n in range(1, num_days):
                    rotated = [rotated[-1]] + rotated[:-1]  # Last round becomes first
                    new_rr_list.extend(rotated)
                rr_list = new_rr_list

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

        # TODO: 6. Check for double missions and apply wished strategy:
        # (a) empty fields, (b) pause, (c) ignore (default)
        if "double_missions" in curr_group_info and curr_group_info["double_missions"] == "empty_field":
            for day in tournament:
                if has_double_missions(day.blocks[group_idx]):  # Check if block has double missions
                    day.blocks[group_idx] = remove_double_missions_with_empty_field(day.blocks[group_idx], num_fields, match_dur)

        elif "double_missions" in curr_group_info and curr_group_info["double_missions"] == "pause":
            pause_dur = curr_group_info["pause_dur"]
            for day in tournament:
                block = day.blocks[group_idx]

                # Resolve parallel double missions first
                block = resolve_parallel_double_missions(block, num_fields, match_dur, pause_dur)

                # Resolve sequential double missions
                prev_teams = set()
                curr_teams = set()
                other_ev_buffer = 0
                insertions = []

                for ev_idx, event in enumerate(block.events):
                    if isinstance(event, MatchEvent):
                        curr_teams = event.get_unique_teams()
                        if has_common_team(prev_teams, curr_teams):
                            curr_pause = pause_dur - other_ev_buffer
                            if curr_pause > 0:
                                pause_event = OtherEvent(curr_pause, "", False, None, None, None, None)
                                insertions.append((ev_idx, pause_event))
                        other_ev_buffer = 0
                        prev_teams = curr_teams
                    elif isinstance(event, OtherEvent):
                        other_ev_buffer += event.duration

                for idx, event in reversed(insertions):
                    block.insert_event_at_position(event, idx)

                day.blocks[group_idx] = block

    # 7. Compact all blocks (remove nones).
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

def has_common_team(prev_teams: set, curr_teams: set) -> bool:
    return not prev_teams.isdisjoint(curr_teams)

def remove_double_missions_with_empty_field(block: EventBlock, num_fields, match_dur):
    new_block = EventBlock()
    # Copy OtherEvents to new block
    for ev_idx, ev in enumerate(block.events):
        if isinstance(ev, OtherEvent):
            new_block.insert_event_at_position(ev, ev_idx)

    # Insert all Matches into new block. Prevent double missions.
    events = block.get_valid_events()
    curr_event = MatchEvent(match_dur, [])
    prev_teams = set()
    other_ev_buffer = 0
    for event in events:
        if isinstance(event, MatchEvent):
            matches = event.matches
            for match in matches:
                # Case 1: team1 or team2 already in current event -> Add empty buffer MatchEvent and start new event
                if (match.team1 in curr_event.get_unique_teams() or match.team2 in curr_event.get_unique_teams()):
                    new_block.add_event_to_next_available_slot(curr_event)
                    new_block.add_event_to_next_available_slot(MatchEvent(match_dur, []))
                    prev_teams = set()
                    curr_event = MatchEvent(match_dur, [match])
                # Case 2: team1 or team2 in previous event -> Start new event
                elif (match.team1 in prev_teams or match.team2 in prev_teams):
                    new_block.add_event_to_next_available_slot(curr_event)
                    prev_teams = curr_event.get_unique_teams()
                    curr_event = MatchEvent(match_dur, [match])
                # Case 3: no double mission -> Append match to current event
                else:
                    curr_event.matches.append(match)
                    
                # If all fields are occupied: Add MatchEvent to block
                if len(curr_event.matches) == num_fields:
                    new_block.add_event_to_next_available_slot(curr_event)
                    prev_teams = curr_event.get_unique_teams()
                    curr_event = MatchEvent(match_dur, [])
            
            other_ev_buffer = 0 # Reset buffer time
        
        elif isinstance(event, OtherEvent):
            other_ev_buffer += event.duration
            # If buffer from OtherEvent(s) is long enough: no empty field needed.
            if other_ev_buffer >= match_dur:
                prev_teams = set()

    # If there remains a partial MatchEvent: Append it to the block as well
    if len(curr_event.matches) > 0:
        new_block.add_event_to_next_available_slot(curr_event)

    return new_block

def has_double_missions(block: EventBlock):
    prev_teams = set()
    curr_teams = set()
    for event in block.events:
        if isinstance(event, MatchEvent):
            curr_teams = event.get_unique_teams()
            if has_common_team(curr_teams, prev_teams):
                return True
            prev_teams = curr_teams
        elif isinstance(event, OtherEvent):
            prev_teams = set()

    return False

def shuffle_with_seed(lst: list, seed: str | int):
    if isinstance(seed, str):
        seed = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % (10**8)
    rng = random.Random(seed)
    shuffled = lst[:]
    rng.shuffle(shuffled)
    return shuffled

def resolve_parallel_double_missions(block: EventBlock, num_fields, match_dur, pause_dur):
    new_block = EventBlock()
    other_ev_buffer = 0

    for ev in block.events:
        if isinstance(ev, MatchEvent):
            curr_event = MatchEvent(match_dur, [])
            conflict_buffer = []
            teams_in_event = set()

            for match in ev.matches:
                # Check if team is already in this event
                if (match.team1 in teams_in_event) or (match.team2 in teams_in_event):
                    # Move to buffer
                    conflict_buffer.append(match)
                else:
                    curr_event.matches.append(match)
                    teams_in_event.update([match.team1, match.team2])

            # Append valid event
            if len(curr_event.matches) > 0:
                new_block.add_event_to_next_available_slot(curr_event)

            # If conflicts existing: Pause, then new event
            if conflict_buffer:
                curr_pause = pause_dur - other_ev_buffer
                if curr_pause > 0:
                    pause_event = OtherEvent(curr_pause, "", False, None, None, None, None)
                    new_block.add_event_to_next_available_slot(pause_event)

                followup_event = MatchEvent(match_dur, conflict_buffer)
                new_block.add_event_to_next_available_slot(followup_event)

            other_ev_buffer = 0

        elif isinstance(ev, OtherEvent):
            new_block.add_event_to_next_available_slot(ev)
            other_ev_buffer += ev.duration
            if other_ev_buffer >= match_dur:
                # Pause is long enough: teams may appear again
                pass

    return new_block
