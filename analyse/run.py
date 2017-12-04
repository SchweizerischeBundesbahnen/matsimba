import logging
import analyse.reader
import os
import pandas as pd
import analyse.plot
import json
import time

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


person_id = "person_id"
mode_trip = "main_mode"
mode_leg = "mode"
column_run = "Run"
trip_id = "journey_id"
leg_id = "trip_id"
distance_field = "distance"
boarding_id = "boarding"
alighting_id = "alighting"

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
    def __init__(self, path, name, scale_factor):
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
            logging.info("Starting loading data %s " % name)
            time1 = time.time()
            sep = keys[name]["sep"]
            path = os.path.join(self.path, keys[name]["path"])
            self.data[name] = pd.read_csv(path, sep=sep, encoding="utf-8", dtype=dtypes).reset_index(drop=True)
            logging.info("%s loaded in %i seconds" % (name,  time.time()-time1))
        except Exception as e:
            logging.error(e.message)

    def load_data(self, with_stop_points=False):
        logging.info("Loading Data for %s" % self.name)
        for name in keys:
            self._load_data(name)
        if with_stop_points:
            self.load_stop_points()

    def merge_trips_persons(self):
        if not self.trip_persons_merged:
            trips = self.get_trips().merge(self.get_persons(), on=person_id, how="left")
            self.trip_persons_merged = True
            self.data["journeys"] = trips
        return self.get_trips()

    def merge_legs_persons(self):
        if not self.legs_persons_merged:
            legs = self.get_legs().merge(self.merge_trips_persons(), on=trip_id, how="left")
            self.legs_persons_merged = True
            self.data["legs"] = legs
        return self.get_legs()

    def merge_link_id_to_name(self, link_id_to_name):
        if not self.link_merged:
            df = self.get_linkvolumes()
            self.data["linkvolumes"] = df.merge(link_id_to_name, on="link_id", how="left")
            self.link_merged = True
        return self.get_linkvolumes()

    def _do(self, df, by, value, foreach=None, aggfunc="count", percent=None, **kwargs):
        if foreach is not None:
            df = df.pivot_table(index=by, columns=foreach, values=value, aggfunc=aggfunc)*self.scale_factor
            if percent:
                df = df.divide(df.sum())
            return df
        else:
            return df.groupby(by).agg({value: aggfunc})*self.scale_factor

    @cache
    def calc_nb_trips(self, by=mode_trip, **kwargs):
        return self._do(self.get_trips(), by=by, value=trip_id, aggfunc="count", **kwargs)

    @cache
    def calc_nb_legs(self, **kwargs):
        return self._do(self.get_legs(), value=leg_id, aggfunc="count", **kwargs)

    @cache
    def calc_dist_trips(self, **kwargs):
        return self._do(self.get_trips(), value=distance_field, aggfunc="sum", **kwargs)

    @cache
    def calc_dist_legs(self, **kwargs):
        return self._do(self.get_legs(), value=distance_field, aggfunc="sum", **kwargs)

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
        df = pd.DataFrame(df[df.boarding_stop != "null"])

        df["CODE"] = df["boarding_stop"].apply(make_code)

        df = self._do(df, value=leg_id, aggfunc="count", **kwargs)

        if codes is not None:
            df = df.loc[codes]

        return df

    @cache
    def calc_vehicles(self, names, **kwargs):
        df = self.get_linkvolumes()
        df = df[df.name.isin(names)]
        df = self._do(df, value="volume", aggfunc="sum", **kwargs)
        return df



