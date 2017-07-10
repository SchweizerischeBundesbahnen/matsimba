import glob
import os
import pandas as pd
import numpy as np
import gzip


def get_persons(folder):
    attributes_file = glob.glob(os.path.join(folder, "*personAttributes.xml.gz"))[0]
    with gzip.open(attributes_file, 'rb') as f:
        file_content = f.read()
        tree_attributes = ET.fromstring(file_content)

        attributes_dict = {}
        for d in tree_attributes.findall("object"):
            _id = d.attrib["id"]
            attributes_dict[_id] = {}
            for dd in d.findall("attribute"):
                attributes_dict[_id][dd.attrib["name"]] = dd.text

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

