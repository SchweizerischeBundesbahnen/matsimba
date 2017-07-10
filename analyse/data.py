import glob
import os
import pandas as pd
import numpy as np
import gzip
import xml.etree.ElementTree as ET


<<<<<<< b374873cb0c59824f600f4c842392ffc2a8dbf22
def get_stops(folder):
    transitfile = glob.glob(os.path.join(folder, "*transitSchedule.xml.gz"))[0]
    
    with gzip.open(transitfile, 'rb') as f:
        file_content = f.read()
        tree = ET.fromstring(file_content)

        stops = []
        for a in tree.findall("transitStops"):
	    for stop in a.findall("stopFacility"):
	        stops.append(stop.attrib)

        return pd.DataFrame.from_dict(stops)

def get_persons(folder, attribute_file=None, persons_file=None):
    if attribute_file is None:
        attributes_file = glob.glob(os.path.join(folder, "*Attributes.xml.gz"))[0]
    with gzip.open(attributes_file, 'rb') as f:
        file_content = f.read()
        tree_attributes = ET.fromstring(file_content)

        attributes_dict = {}
        for d in tree_attributes.findall("object"):
            _id = d.attrib["id"]
            attributes_dict[_id] = {}
            for dd in d.findall("attribute"):
                attributes_dict[_id][dd.attrib["name"]] = dd.text

        if persons_file is None:
            persons_file = glob.glob(os.path.join(folder, "*plans.xml.gz"))[0]
        with gzip.open(persons_file, 'rb') as f:
            file_content = f.read()
            tree = ET.fromstring(file_content)

            persons = []
            for p in tree.findall("person"):
                d = p.attrib
                score = None
                if d["id"] in attributes_dict:
                    d = dict(d.items() + attributes_dict[d["id"]].items())

                for a in p.findall("plan"):
                    if a.attrib["selected"] == "yes":
                        score = a.attrib["score"]

                d["score"] = score
                persons.append(d)

            return pd.DataFrame.from_dict(persons)


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

