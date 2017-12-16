import logging
import analyse.reader
import os
import pandas as pd
import analyse.plot
import json
import time
import numpy as np
import analyse.skims
from variable import *

_cache = {}


def clear_cache():
    _cache.clear()


def cache(func):
    " Used on methods to convert them to methods that replace themselves\
        with their return value once they are called. "

    def f(*args, **kwargs):
        self = args[0]  # Reference to the class who owns the method
        funcname = func.__name__
        key = (self, funcname, args) + tuple(json.dumps(kwargs, sort_keys=True))
        if key not in _cache:
            _cache[key] = func(*args, **kwargs)
        else:
            logging.info("Loading from cache :). Use clear_cache")
        return _cache[key]

    return f


keys = {"acts":
            {"path": "matsim_activities.txt", "sep": "\t"},
        "journeys":
            {"path": "matsim_journeys.txt", "sep": "\t"},
        "legs":
            {"path": "matsim_trips.txt", "sep": "\t"},
        "vehjourneys":
            {"path": "matsim_vehjourneys.csv", "sep": ";"},
        "stops":
            {"path": "matsim_stops.csv", "sep": ";"},
        "linkvolumes":
            {"path": "matsim_linkvolumes.csv", "sep": ";"},
        "planelements":
            {"path": "plan_elements.csv", "sep": ";"},
        "persons":
            {"path": "agents.csv", "sep": ";"}}


def _start_logging():
    logger = logging.getLogger()

    for handler in logger.handlers:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


_start_logging()
analyse.plot.set_matplotlib_params()

dtypes = {u'activity_id': str,
          u'person_id': str,
          u'trip_id': str,
          u'boarding_stop': str,
          u'alighting': str,
          u'link_id': str,
          u'work': str,
          u'season_ticket': str,
          u'subpopulation': str,
          u'employed': str,
          u'carAvail': str,
          u"gender": str,
          u"work: employment status": str,
          u"sex": str,
          u"hasLicense": str}


class Run:
    def __init__(self, path=None, name=None, scale_factor=1.0):
        self.path = path
        self.name = name
        self.scale_factor = scale_factor

        self.data = {}

        self.trip_persons_merged = False
        self.legs_persons_merged = False
        self.link_merged = False

    def get_persons(self):
        return self._get("persons")

    def get_acts(self):
        return self._get("acts")

    def get_trips(self):
        return self._get("journeys")

    def get_legs(self):
        return self._get("legs")

    def get_vehjourneys(self):
        return self._get("vehjourneys")

    def get_boarding_alighting(self):
        return self._get("stops")

    def get_stops(self):
        return self.get_boarding_alighting()

    def get_ea(self):
        return self.get_boarding_alighting()

    def get_linkvolumes(self):
        return self._get("linkvolumes")

    def get_planelements(self):
        return self._get("planelements")

    def get_stop_points(self):
        return self._get("stop_points")

    def _get(self, name, reload_data=False):
        self._load_data(name, reload_data=reload_data)
        return self.data[name]

    def load_stop_points(self):
        self.data["stop_points"] = analyse.reader.get_stops(self.path)

    def _load_data(self, name, reload_data=True):
        if not reload_data and name in self.data:
            logging.debug("Data %s already loaded" % name)
            return

        try:
            time1 = time.time()
            sep = keys[name]["sep"]
            path = os.path.join(self.path, keys[name]["path"])
            logging.info("Starting loading data %s: %s " % (name, path))
            self.data[name] = pd.read_csv(path, sep=sep, encoding="utf-8", dtype=dtypes).reset_index(drop=True)
            logging.info("%s loaded in %i seconds" % (name, time.time() - time1))
        except Exception as e:
            logging.error(e.message)

    def unload_data(self):
        self.data.clear()
        self.trip_persons_merged = False
        self.legs_persons_merged = False
        self.link_merged = False

    def load_data(self, with_stop_points=False):
        logging.info("Loading Data for %s" % self.name)
        for name in keys:
            self._load_data(name)
        if with_stop_points:
            self.load_stop_points()

    def _set_dummy_pf(self):
        df = self.get_legs()
        df[PF] = 1.0
        df[PKM] = df[DISTANCE]

        df = self.get_trips()
        df[PF] = 1.0
        df[PKM] = df[DISTANCE]

    def prepare(self, stop_ids_perimeter, defining_stop_ids):
        self.unload_data()

        df = self.get_legs()

        df = df[df.line.notnull()]
        fq_legs = analyse.skims.filter_legs_to_binnenverkehr_fq_legs(df, stop_ids_perimeter=stop_ids_perimeter,
                                                                     defining_stop_ids=defining_stop_ids)

        df[IS_SIMBA_FQ] = False
        df.loc[df.trip_id.isin(fq_legs.trip_id), IS_SIMBA_FQ] = True

        df = self.merge_trips_persons()
        df = self.merge_legs_persons()

        df = self.get_trips()

        df.loc[df.main_mode == TRANSIT_WALK, MAIN_MODE] = WALK_AGGR
        df.loc[df.main_mode == WALK, MAIN_MODE] = WALK_AGGR

        self._set_dummy_pf()

    def merge_trips_persons(self):
        if not self.trip_persons_merged:
            trips = self.get_trips().merge(self.get_persons(), on=person_id, how="left", suffixes=("", "_p"))
            self.trip_persons_merged = True
            self.data["journeys"] = trips
        return self.get_trips()

    def merge_legs_persons(self):
        if not self.legs_persons_merged:
            legs = self.get_legs().merge(self.merge_trips_persons(), on=trip_id, how="left", suffixes=("", "_trips"))
            self.legs_persons_merged = True
            self.data["legs"] = legs
        return self.get_legs()

    def merge_link_id_to_name(self, link_id_to_name):
        if not self.link_merged:
            df = self.get_linkvolumes()
            self.data["linkvolumes"] = df.merge(link_id_to_name, on="link_id", how="left")
            self.link_merged = True
        return self.get_linkvolumes()

    def _do(self, df, by, value, foreach=None, aggfunc="count", percent=None, inverse_percent_axis=False, **kwargs):
        def check_variable(values):
            if not isinstance(values, list):
                values = [values]
            for _value in values:
                if _value not in df.columns:
                    df[_value] = "Undefined"

        def make_percent(df):
            if inverse_percent_axis:
                df = df.divide(df.sum(axis=1), axis=0)
            else:
                df = df.divide(df.sum())
            return df

        check_variable(by)
        check_variable(foreach)

        if foreach is not None:
            df = df.pivot_table(index=by, columns=foreach, values=value, aggfunc=aggfunc) * self.scale_factor
        else:
            df = df.groupby(by).agg({value: aggfunc}) * self.scale_factor

        if percent:
            df = make_percent(df)

        return df.fillna(0)

    @cache
    def calc_nb_trips(self, by=mode_trip, **kwargs):
        return self._do(self.get_trips(), by=by, value=PF, aggfunc="sum", **kwargs)

    @cache
    def calc_nb_legs(self, **kwargs):
        return self._do(self.get_legs(), value=PF, aggfunc="sum", **kwargs)

    @cache
    def calc_dist_trips(self, **kwargs):
        return self._do(self.get_trips(), value=PKM, aggfunc="sum", **kwargs)

    @cache
    def calc_dist_legs(self, **kwargs):
        return self._do(self.get_legs(), value=PKM, aggfunc="sum", **kwargs)

    @cache
    def calc_dist_distr_trips(self, inverse_percent_axis=False, rotate=True, **kwargs):
        self.create_distance_class_for_trips()
        df = self._do(self.get_trips(), by=CAT_DIST, value=PF, aggfunc="sum", rotate=rotate,
                      inverse_percent_axis=inverse_percent_axis, **kwargs)
        if inverse_percent_axis:
            return df
        else:
            return df.cumsum()

    @cache
    def calc_dist_distr_legs(self, inverse_percent_axis=False, rotate=True, **kwargs):
        self.create_distance_class_for_legs()
        df = self._do(self.get_legs(), by=CAT_DIST, value=PF, aggfunc="sum", rotate=rotate,
                      inverse_percent_axis=inverse_percent_axis, **kwargs)
        if inverse_percent_axis:
            return df
        else:
            return df.cumsum()

    def plot_timing(self):
        analyse.plot.plot_timing(self.path)

    def plot_score(self):
        analyse.plot.plot_score([self.path])

    @cache
    def calc_einsteiger(self, codes=None, **kwargs):
        def make_code(stop_id):
            a = stop_id.split("_")
            if len(a) == 2:
                return a[1]
            else:
                return None

        df = self.get_legs()
        df = pd.DataFrame(df[df.boarding_stop.notnull()])

        df[CODE] = df[BOARDING_STOP].apply(make_code)

        df = self._do(df, value=leg_id, aggfunc="count", **kwargs)

        if codes is not None:
            df = df.loc[codes]

        return df

    @cache
    def calc_vehicles(self, names=None, **kwargs):
        df = self.get_linkvolumes()
        df = self._do(df, value=VOLUME, aggfunc="sum", **kwargs)
        if names is not None:
            df = df.loc[names]
        return df

    @staticmethod
    def _create_distance_class(df, column=DISTANCE, classes=None, labels=None, category_column=CAT_DIST):
        if classes is None:
            classes = np.array(
                [-1, 0, 2, 4, 6, 8, 10, 15, 20, 25, 30, 40, 50, 100, 150, 200, 250, 300, np.inf]) * 1000.0
            labels = []
            for i in range(len(classes) - 2):
                labels.append("%i-%i km" % (classes[i] / 1000.0, classes[i + 1] / 1000.0))
            labels.append("-")

        df[category_column] = pd.cut(df[column], classes, labels=labels)

    def create_distance_class_for_legs(self, **kwargs):
        self._create_distance_class(self.get_legs(), **kwargs)

    def create_distance_class_for_trips(self, **kwargs):
        self._create_distance_class(self.get_trips(), **kwargs)
