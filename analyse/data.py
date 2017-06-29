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
