#!/usr/bin/env python
# -*- coding: cp1252-*-
import pandas as pd
import logging
from analyse.variable import IS_SIMBA, JOURNEY_ID, TRIP_ID, BOARDING_STOP, START_TIME, ALIGHTING_STOP, END_TIME, STOP_ID
from vimapy.helpers import hhmmss_to_seconds, seconds_to_hhmmss

pd.options.mode.chained_assignment = None


# noinspection PyShadowingNames
def set_is_simba_leg(df_legs, routes_simba):
    logging.info("setting is_simba")
    if not IS_SIMBA in df_legs.columns:
        df_legs[IS_SIMBA] = df_legs.route.apply(lambda x: x in routes_simba)

    logging.info("done setting is_simba")
    return df_legs


def set_binnenverkehr_attributes(df_legs, stops_in_perimeter):
    # get information of first leg per journey
    stops_in_perimeter = set(stops_in_perimeter)
    logging.info("setting binnernverkehr attributes")
    df_legs_filtered = df_legs[df_legs[IS_SIMBA]]
    first_leg = df_legs_filtered[[JOURNEY_ID, TRIP_ID]].groupby(JOURNEY_ID).min().reset_index()
    first_leg.columns = [JOURNEY_ID, "start_id"]
    first_leg = first_leg.merge(df_legs_filtered, left_on=[JOURNEY_ID, "start_id"], right_on=[JOURNEY_ID, TRIP_ID])
    first_leg = first_leg[[JOURNEY_ID, "start_id", BOARDING_STOP, START_TIME]]
    first_leg.columns = [JOURNEY_ID, "start_id", "first_stop", "start_time_first_stop"]

    logging.info("get information of last leg per journey")
    # get information of last leg per journey
    last_leg = df_legs_filtered[[JOURNEY_ID, TRIP_ID]].groupby(JOURNEY_ID).max().reset_index()
    last_leg.columns = [JOURNEY_ID, "last_id"]
    last_leg = last_leg.merge(df_legs_filtered, left_on=[JOURNEY_ID, "last_id"], right_on=[JOURNEY_ID, TRIP_ID])
    last_leg = last_leg[[JOURNEY_ID, "last_id", ALIGHTING_STOP, END_TIME]]
    last_leg.columns = [JOURNEY_ID, "last_id", "last_stop", "end_time_last_stop"]

    logging.info("combine information on first and last leg per journey")
    # combine information on first and last leg per journey
    first_last_leg_info = first_leg.merge(last_leg, on=JOURNEY_ID)
    first_last_leg_info["start_simba_stop_in_perimeter"] = first_last_leg_info["first_stop"].isin(stops_in_perimeter)
    first_last_leg_info["last_simba_stop_in_perimeter"] = first_last_leg_info["last_stop"].isin(stops_in_perimeter)
    nb_legs_before = len(df_legs)
    df_legs = df_legs.merge(first_last_leg_info, on=JOURNEY_ID, how="left") # TODO: merge possible with inplace? => DM
    if len(df_legs) != nb_legs_before:
        raise ValueError(
            "nb of legs changed. before: {}. after: {}".format(nb_legs_before, len(df_legs)))
    df_legs["is_binnenverkehr_simba"] = df_legs["start_simba_stop_in_perimeter"] & df_legs["last_simba_stop_in_perimeter"]
    logging.info("done setting binnernverkehr attributes")
    return df_legs


def set_is_fq_journey(df_legs, defining_stop_ids):
    logging.info("setting fq journey attributes")
    defining_stop_ids = set(defining_stop_ids)
    df_legs_filered = df_legs[df_legs[IS_SIMBA] & df_legs["is_binnenverkehr_simba"]]
    df_legs_filered["leg_is_fq"] = df_legs_filered[BOARDING_STOP].isin(defining_stop_ids) & \
                                   df_legs_filered[ALIGHTING_STOP].isin(defining_stop_ids)
    has_fq_leg = (df_legs_filered[[JOURNEY_ID, "leg_is_fq"]]).groupby(JOURNEY_ID).max()
    has_fq_leg = has_fq_leg.reset_index()
    has_fq_leg.columns = [JOURNEY_ID, "journey_has_fq_leg"]
    nb_legs_before = len(df_legs)
    df_legs = df_legs.merge(has_fq_leg, on=JOURNEY_ID, how="left")
    if len(df_legs) != nb_legs_before:
        raise ValueError(
            "nb of legs changed. before: {}. after: {}".format(len(df_legs), nb_legs_before))
    logging.info("done setting fq journey attributes")
    return df_legs


def set_simba_binnenverkehr_fq_attributes(df_legs, stop_ids_perimeter, stop_ids_fq, routes_simba):
    df_legs.sort_values([JOURNEY_ID, TRIP_ID], inplace=True)
    df_legs_simba = set_is_simba_leg(df_legs, routes_simba)
    df_legs_simba_binnenverkehr = set_binnenverkehr_attributes(df_legs_simba, stop_ids_perimeter)
    df = set_is_fq_journey(df_legs_simba_binnenverkehr, stop_ids_fq)
    return df


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
    skim_per_station_to_station["bz"] = (skim_per_station_to_station["weighted_bz"] / \
                                        skim_per_station_to_station[
                                            "PFAHRT"]).apply(float)
    skim_per_station_to_station["bz_hhmmss"] = skim_per_station_to_station["bz"].apply(seconds_to_hhmmss)
    skim_per_station_to_station["uh"] = skim_per_station_to_station["weighted_uh"] / \
                                        skim_per_station_to_station[
                                            "PFAHRT"]
    skim_per_station_to_station["distance"] = skim_per_station_to_station["weighted_distance"] / \
                                              skim_per_station_to_station["PFAHRT"]
    skim_per_station_to_station["distance"] /= 1000.0
    skim_per_station_to_station = skim_per_station_to_station.reset_index()
    skim_per_station_to_station = skim_per_station_to_station.sort_values("PFAHRT", ascending=False)
    cols_out = ["first_stop", "last_stop", "PFAHRT", "bz", "bz_hhmmss", "uh", "distance"]
    return skim_per_station_to_station[cols_out]


def read_matsim_trips(path_matsim_trips):
    return pd.read_csv(path_matsim_trips, sep="\t")

