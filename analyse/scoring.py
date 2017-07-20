import math
import xml.etree.ElementTree
import pandas as pd
import numpy as np


def load_config(config_path):
    my_dict = {}
    e = xml.etree.ElementTree.parse(config_path).getroot()

    my_dict["modes"] = {}
    my_dict["activities"] = {}

    m = [m for m in e.findall("module") if m.attrib["name"] == "planCalcScore"][0].findall("parameterset")[0]
    for _m in m.findall("param"):
        my_dict[_m.attrib["name"]] = _m.attrib["value"]

    for _m in m.findall("parameterset"):
        _my_dict = {}
        for __m in _m.findall("param"):
            _my_dict[__m.attrib["name"]] = __m.attrib["value"]

        if "mode" in _my_dict:

            my_dict["modes"][_my_dict["mode"]] = _my_dict
        elif "activityType" in _my_dict:
            my_dict["activities"][_my_dict["activityType"]] = _my_dict
    return my_dict


def t0_q(t_typ_q, prio=1.0):
    return t_typ_q * math.exp(-10 * 60 * 60.0 / (prio * t_typ_q))


def make_sdur(x, acts_param, b_dur):
    typical_duration = t_typ_q[x["type"]]
    zero_utility_duration = t0_q(t_typ_q[x["type"]])
    duration = x["end_time"] - x["start_time"]
    if duration >= zero_utility_duration:
        return b_dur * t_typ_q[x["type"]] * math.log((x["end_time"] - x["start_time"]) / t0_q(t_typ_q[x["type"]]))
    else:
        slope = b_dur * typical_duration / zero_utility_duration

        return -slope * (zero_utility_duration - duration)


def make_legscore(p, marginalUtilityOfMoney):
    def f(x):
        if (x["end_time"] - x["start_time"]) <= 0:
            return 0.0

        t_trav = x["end_time"] - x["start_time"]
        d_trav = x["distance"]

        mode = x["mode"]
        if mode == "transit_walk":
            mode = "walk"
        return p["c"] + p["marginalUtilityOfTravelling_util_hr"] * t_trav / 60.0 / 60.0 + p["monetaryDistanceRate"] * d_trav * marginalUtilityOfMoney
    return f


def compute(persons, acts_df, legs_df, journeys_df, p_id, config_path, end_time=35*60*60):

    config = load_config(config_path)

    _acts_df = pd.DataFrame(acts_df)
    _acts_df.set_index("activity_id", inplace=True)
    _acts_df[_acts_df.person_id == p_id].head()

    start_act = _acts_df[_acts_df.start_time == 0.0].reset_index().set_index("person_id")
    end_act = _acts_df[_acts_df.end_time == end_time].reset_index().set_index("person_id")

    start_act.start_time = end_act.start_time - 24 * 60 * 60

    _acts_df.drop(end_act.activity_id, inplace=True)
    _acts_df.drop(start_act.activity_id, inplace=True)

    _acts_df = pd.concat([_acts_df, start_act.reset_index().set_index("activity_id")])
    _acts_df["acts_scores"] = _acts_df.apply(make_sdur, axis=1)

    legs_df["travel_scores"] = legs_df.apply(make_legscore(config["modes"]), axis=1)

    res = legs_df[legs_df["mode"] == "pt"].groupby("journey_id").count()[["start_time"]]
    res.rename(columns={'start_time': 'transfers'}, inplace=True)
    res["transfers"] += - 1.0
    res["score_transfer"] = b_transf * (res["transfers"])

    legs_df["duration_legs"] = legs_df["end_time"] - legs_df["start_time"]
    journeys_df["duration"] = journeys_df["end_time"] - journeys_df["start_time"]
    _df = pd.concat([journeys_df, res, legs_df.groupby("journey_id")[["travel_scores"]].sum(),
                     legs_df.groupby("journey_id")[["duration_legs"]].sum()], axis=1)

    _df.loc[np.isnan(_df.score_transfer), "score_transfer"] = 0.0
    _df.loc[np.isnan(_df.transfers), "transfers"] = 0.0

    _df["waiting_time"] = _df["duration"] - _df["duration_legs"]
    _df["total_travel_scores"] = _df["score_transfer"] + _df["travel_scores"] + _df["waiting_time"] / 60.0 / 60.0 * waitingPt - _df["transfers"] * modes["pt"]["c"]

    scores = pd.concat([persons,
                        _df.groupby("person_id").total_travel_scores.sum(),
                        _acts_df.groupby("person_id")["acts_scores"].sum()], axis=1)

    return scores, _df, _acts_df