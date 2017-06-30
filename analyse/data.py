import glob
import os
import pandas as pd


def get_activities(folder):
    filename = os.path.join(folder, "matsim_activities.txt")
    return pd.DataFrame.from_csv(filename, sep="\t")


def get_legs(folder):
    filename = os.path.join(folder, "matsim_trips.txt")
    legs = pd.DataFrame.from_csv(filename, sep="\t")
    legs["duration"] = legs.end_time-legs.start_time
    return legs


def get_trips(folder):
    filename = os.path.join(folder, "matsim_journeys.txt")
    return pd.DataFrame.from_csv(filename, sep="\t")


def get_legs(folder):
    filename = os.path.join(folder, "matsim_trips.txt")
    legs = pd.DataFrame.from_csv(filename, sep="\t")
    legs["duration"] = legs.end_time-legs.start_time
    return legs


def get_legs_sum(folder):
    legs = get_legs(folder)
    return legs.groupby("mode").sum()[["distance", "duration"]]


def merge_journeys_with_acts(acts, journeys):
    _acts = acts[["type", "zone", "activity_id"]]
    _acts = _acts.rename(columns={'type': 'act_type', 'zone': 'act_zone'})

    merged = journeys.merge(_acts, left_on="from_act", right_on="activity_id")
    merged = merged.merge(_acts, left_on="to_act", suffixes=("_from", "_to"), right_on="activity_id")
    return merged[np.logical_and(merged.act_zone_from != "undefined", merged.act_zone_to != "undefined" )]

