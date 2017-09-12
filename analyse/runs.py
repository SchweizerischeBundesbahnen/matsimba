import pandas as pd
from collections import defaultdict
import os
import logging
import analyse.data


class RunsDatabase:
    def __init__(self, path):
        self.path = path
        self.data = defaultdict(dict)
        self.db = None
        self.rescan()

    def rescan(self):
        db = pd.read_csv(self.path)
        db.set_index(["Name"], inplace=True)
        self.db = db

    def get_paths(self, names):
        return [self.get_path(k) for k in names]

    def get_path(self, name):
        return self.db.loc[name].Path

    def load_data(self, only_new=True, names=None, with_stop_points=False):
        if names is None:
            names = self.db.index
        for name in names:
            if only_new:
                if name not in self.data:
                    self._load_data(name, with_stop_points=with_stop_points)
            else:
                self._load_data(name, with_stop_points=with_stop_points)

    def load_stop_points(self, run_name):
        _path = self.get_path(run_name)
        self.data[run_name]["stop_points"] = analyse.data.get_stops(_path)

    def _load_data(self, run_name, with_stop_points):
        logging.info("Laoding Data for %s" % run_name)
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
        _path = self.get_path(run_name)
        for name in keys:
            try:
                sep = keys[name]["sep"]
                path = os.path.join(_path, keys[name]["path"])
                self.data[run_name][name] = pd.DataFrame.from_csv(path, sep=sep, encoding="utf-8").reset_index()
            except Exception as e:
                logging.error(e.message)
        if with_stop_points:
            self.load_stop_points(run_name)

    def get(self, sim_name, name):
        return self.data[sim_name][name]

    def get_persons(self, sim_name):
        return self.get(sim_name, "persons")

    def get_acts(self, sim_name):
        return self.get(sim_name, "acts")

    def get_trips(self, sim_name):
        return self.get(sim_name, "journeys")

    def get_legs(self, sim_name):
        return self.get(sim_name, "legs")

    def get_vehjourneys(self, sim_name):
        return self.get(sim_name, "vehjourneys")

    def get_boarding_alighting(self, sim_name):
        return self.get(sim_name, "stops")

    def get_stops(self, sim_name):
        return self.get_boarding_alighting(sim_name)

    def get_ea(self, sim_name):
        return self.get_boarding_alighting(sim_name)

    def get_linkvolumes(self, sim_name):
        return self.get(sim_name, "linkvolumes")

    def get_planelements(self, sim_name):
        return self.get(sim_name, "planelements")

    def get_stop_points(self, sim_name):
        return self.get(sim_name, "stop_points")



