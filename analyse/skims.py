#!/usr/bin/env python
# -*- coding: cp1252-*-
import pandas as pd

from vimapy.helpers import hhmmss_to_seconds, seconds_to_hhmmss

pd.options.mode.chained_assignment = None

FPFE_START_HP_CODE = "STARTFAHRPLANFAHRTELEMENT\FZPELEMENT\LINIENROUTENELEMENT\HALTEPUNKT\CODE"
FPFE_END_HP_CODE = "ENDFAHRPLANFAHRTELEMENT\FZPELEMENT\LINIENROUTENELEMENT\HALTEPUNKT\CODE"


required_attributes = {"journey_id", "start_time", "end_time", "boarding_stop", "alighting_stop"}
required_attributes_visum = {"LINNAME", "$OEVTEILWEG:QBEZNR", "ZBEZNR", "WEGIND", "VONHPUNKTNR",
                             FPFE_START_HP_CODE,
                             "NACHHPUNKTNR",
                             FPFE_END_HP_CODE,
                             "ABFAHRT", "ANKUNFT",
                             "TWEGIND", "PFAHRT", "WEITE"}


def is_simba_line(line_id):
    # a hack: we assume that simba-lines are coded as 041-A-01102_GEAP-BI-ZUE-SG_Bas120_[H]
    splitted = line_id.split("_")
    if len(splitted) <= 1:
        return False
    else:
        first = splitted[0]
        splitted_againg = first.split("-")
        if len(splitted_againg) == 3:
            return True
        else:
            return False


def test_columns_of_legs(df_legs, required_attr, from_simba_visum=False):
    if from_simba_visum:
        required_attr = required_attr.union({"TWEGIND"})
    if required_attr not in set(df_legs.columns):
        missing_attributes = required_attr - set(df_legs)
        if len(missing_attributes) > 0:
            raise AttributeError(
                "following columns in input-dataframe are required: {}".format(list(missing_attributes)))


def prepare_oevteilwege_visum(df_oevteilwege_input):
    """renames and recalculates the columns of oevteilwege from visum such that the resulting data-frame
    has the same structure as a leg-dataframe from matsim"""
    test_columns_of_legs(df_oevteilwege_input, required_attributes_visum)
    df_oevteilwege = df_oevteilwege_input[df_oevteilwege_input["LINNAME"].notnull()]
    df_oevteilwege["journey_id"] = df_oevteilwege["$OEVTEILWEG:QBEZNR"].map(str) + "_" + \
                                   df_oevteilwege_input["ZBEZNR"].map(str) + "_" + \
                                   df_oevteilwege_input["WEGIND"].map(str)
    df_oevteilwege["boarding_stop"] = df_oevteilwege["VONHPUNKTNR"].map(int).map(str) + "_" + \
                                      df_oevteilwege_input[FPFE_START_HP_CODE]
    df_oevteilwege["alighting_stop"] = df_oevteilwege["NACHHPUNKTNR"].map(int).map(str) + "_" + \
                                       df_oevteilwege_input[FPFE_END_HP_CODE]
    df_oevteilwege["start_time"] = df_oevteilwege["ABFAHRT"].map(hhmmss_to_seconds)
    df_oevteilwege["end_time"] = df_oevteilwege["ANKUNFT"].map(hhmmss_to_seconds)
    new_cols = ["journey_id", "TWEGIND", "boarding_stop", "alighting_stop", "PFAHRT", "LINNAME", "start_time",
                "end_time", "WEITE"]
    df_oevteilwege = df_oevteilwege[new_cols]
    df_oevteilwege.columns = ["journey_id", "TWEGIND", "boarding_stop", "alighting_stop", "PFAHRT",
                                    "line", "start_time", "end_time", "distance"]
    return df_oevteilwege


# noinspection PyShadowingNames
def filter_to_simba_legs(df_legs, is_simba_line, from_simba_visum=False):
    test_columns_of_legs(df_legs, required_attributes, from_simba_visum=from_simba_visum)
    if not from_simba_visum:
        legs_simba = df_legs[df_legs.line.apply(is_simba_line)].sort_values(by=["journey_id", "start_time"])
    else:
        legs_simba = df_legs
    return legs_simba


def filter_to_binnenverkehr(df_legs, stops_in_perimeter, from_simba_visum=False):
    test_columns_of_legs(df_legs, required_attributes, from_simba_visum=from_simba_visum)
    # get information of first leg per journey
    if from_simba_visum:
        # if from_simba_visum start- or end-times are always < 24*60*60
        first_leg = df_legs[["journey_id", "TWEGIND"]].groupby("journey_id").min().reset_index()
    else:
        first_leg = df_legs[["journey_id", "start_time"]].groupby("journey_id").min().reset_index()
    first_leg.columns = ["journey_id", "start_id"]

    if from_simba_visum:
        first_leg = first_leg.merge(df_legs, left_on=["journey_id", "start_id"],
                                    right_on=["journey_id", "TWEGIND"])
    else:
        first_leg = first_leg.merge(df_legs, left_on=["journey_id", "start_id"],
                                    right_on=["journey_id", "start_time"])
    first_leg = first_leg[["journey_id", "start_id", "boarding_stop", "start_time"]]
    first_leg.columns = ["journey_id", "start_id", "first_stop", "start_time_first_stop"]

    # get information of last leg per journey
    if from_simba_visum:
        last_leg = df_legs[["journey_id", "TWEGIND"]].groupby("journey_id").max().reset_index()
    else:
        last_leg = df_legs[["journey_id", "end_time"]].groupby("journey_id").max().reset_index()
    last_leg.columns = ["journey_id", "end_id"]

    if from_simba_visum:
        last_leg = last_leg.merge(df_legs, left_on=["journey_id", "end_id"],
                                  right_on=["journey_id", "TWEGIND"])
    else:
        last_leg = last_leg.merge(df_legs, left_on=["journey_id", "end_id"],
                                  right_on=["journey_id", "end_time"])
    last_leg = last_leg[["journey_id", "end_id", "alighting_stop", "end_time"]]
    last_leg.columns = ["journey_id", "end_id", "last_stop", "end_time_last_stop"]

    # combine information on first and last leg per journey
    first_last_leg_info = first_leg.merge(last_leg, on="journey_id")
    first_last_leg_info["start_in_cnb"] = first_last_leg_info["first_stop"].isin(stops_in_perimeter)
    first_last_leg_info["end_in_cnb"] = first_last_leg_info["last_stop"].isin(stops_in_perimeter)
    df_legs_merged = df_legs.merge(first_last_leg_info, on="journey_id", how="left")
    if len(df_legs_merged) != len(df_legs):
        raise ValueError(
            "nb of legs changed. before: {}. after: {}".format(len(df_legs), len(df_legs_merged)))
    return df_legs_merged[(df_legs_merged.start_in_cnb & df_legs_merged.end_in_cnb)]


def filter_to_journeys_with_at_least_one_leg_in_defining_stops(df_legs, defining_stop_ids):
    cols = df_legs.columns
    df_legs["boarding_stop_is_defining_stop"] = df_legs["boarding_stop"].isin(defining_stop_ids)
    has_defining_leg = (df_legs[["journey_id", "boarding_stop_is_defining_stop"]]).groupby("journey_id").max()
    has_defining_leg = has_defining_leg.reset_index()
    df_legs_merged = df_legs.merge(has_defining_leg, on="journey_id", how="left")
    if len(df_legs_merged) != len(df_legs):
        raise ValueError(
            "nb of legs changed. before: {}. after: {}".format(len(df_legs), len(df_legs_merged)))
    df_legs_res = df_legs_merged[df_legs_merged["boarding_stop_is_defining_stop_y"]]
    return df_legs_res[cols]


def filter_legs_to_binnenverkehr_fq_legs(df_legs, stop_ids_perimeter, defining_stop_ids,
                                         from_simba_visum=False):
    df_legs_simba = filter_to_simba_legs(df_legs, is_simba_line, from_simba_visum=from_simba_visum)
    df_legs_simba_binnenverkehr = filter_to_binnenverkehr(df_legs_simba, stop_ids_perimeter,
                                                          from_simba_visum=from_simba_visum)
    return filter_to_journeys_with_at_least_one_leg_in_defining_stops(
        df_legs_simba_binnenverkehr,
        defining_stop_ids)


def get_station_to_station_skims(df_legs, factor=1.0, from_simba_visum=False):
    if not from_simba_visum:
        df_legs["PFAHRT"] = factor
    start_time_per_journey = df_legs[["journey_id", "start_time_first_stop"]].groupby("journey_id").min()
    start_time_per_journey = start_time_per_journey.reset_index()
    end_time_per_journey = df_legs[["journey_id", "end_time_last_stop"]].groupby("journey_id").max()
    end_time_per_journey = end_time_per_journey.reset_index()

    skim_per_journey = start_time_per_journey.merge(end_time_per_journey, on="journey_id")
    skim_per_journey["bz"] = skim_per_journey["end_time_last_stop"] - skim_per_journey[
        "start_time_first_stop"]
    skim_per_journey["bz"] = skim_per_journey["bz"].apply(lambda x: x if x >= 0 else x + 24 * 60 * 60)

    uh_per_journey = df_legs[["journey_id", "start_time"]].groupby("journey_id").count()
    uh_per_journey = uh_per_journey.reset_index()
    uh_per_journey.columns = ["journey_id", "uh"]
    uh_per_journey["uh"] -= 1.0
    skim_per_journey = skim_per_journey.merge(uh_per_journey, on="journey_id")

    pf_per_journey = df_legs[["journey_id", "PFAHRT"]].groupby("journey_id").min()
    pf_per_journey = pf_per_journey.reset_index()
    skim_per_journey = skim_per_journey.merge(pf_per_journey, on="journey_id")

    distance_per_journey = df_legs[["journey_id", "distance"]].groupby("journey_id").sum()
    distance_per_journey = distance_per_journey.reset_index()
    skim_per_journey = skim_per_journey.merge(distance_per_journey, on="journey_id")

    skim_per_journey["weighted_bz"] = skim_per_journey["PFAHRT"] * skim_per_journey["bz"]
    skim_per_journey["weighted_uh"] = skim_per_journey["PFAHRT"] * skim_per_journey["uh"]
    skim_per_journey["weighted_distance"] = skim_per_journey["PFAHRT"] * skim_per_journey["distance"]

    first_last_stop_per_journey = df_legs[["journey_id", "first_stop", "last_stop"]].groupby(
        "journey_id").min()
    first_last_stop_per_journey = first_last_stop_per_journey.reset_index()
    skim_per_journey = skim_per_journey.merge(first_last_stop_per_journey, on="journey_id")

    skim_per_station_to_station = skim_per_journey[
        ["first_stop", "last_stop", "PFAHRT", "weighted_bz", "weighted_uh", "weighted_distance"]].groupby(
        ["first_stop", "last_stop"]).sum()
    skim_per_station_to_station["bz"] = skim_per_station_to_station["weighted_bz"] / \
                                        skim_per_station_to_station[
                                            "PFAHRT"]
    skim_per_station_to_station["bz_hhmmss"] = skim_per_station_to_station["bz"].apply(seconds_to_hhmmss)
    skim_per_station_to_station["uh"] = skim_per_station_to_station["weighted_uh"] / \
                                        skim_per_station_to_station[
                                            "PFAHRT"]
    skim_per_station_to_station["distance"] = skim_per_station_to_station["weighted_distance"] / \
                                              skim_per_station_to_station["PFAHRT"]
    skim_per_station_to_station["distance"] /= 1000.0
    skim_per_station_to_station = skim_per_station_to_station.reset_index()
    skim_per_station_to_station = skim_per_station_to_station.sort_values(by="PFAHRT", ascending=False)
    cols_out = ["first_stop", "last_stop", "PFAHRT", "bz", "bz_hhmmss", "uh", "distance"]
    return skim_per_station_to_station[cols_out]
