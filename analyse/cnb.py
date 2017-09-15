import analyse.mergers
import pandas as pd
import numpy as np


def filter_inact(df):
    return df[df.subpopulation == "regular_inAct"]


def make_simba_code(stops, run , code_field="CODE", field="stop_id"):
    stops["is_simba"] = stops.line.str.match(r'\d{3}-[A-Z]-.*')
    stops[code_field] = None
    stops.loc[stops.is_simba, code_field] = stops[stops.is_simba][field].apply(lambda x: x.split("_")[1])
    return stops


def cut_distance(df, run):
    df = analyse.mergers.trips_with_persons(df, run)
    df = filter_inact(df)
    df["cat_dist"] = pd.cut(df.distance, np.array([0,2,4,6,8,10,15,20,25,30,40,50, np.inf])*1000.0)
    return df