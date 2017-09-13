import pandas as pd
from collections import defaultdict
import os
import logging
import analyse.data


class Run:
    def __init__(self, path, name, scale_factor):
        self.path = path
        self.name = name
        self.scale_factor = scale_factor

        self.data = {}

    def get_persons(self):
        return self.data["persons"]

    def get_acts(self):
        return self.data["acts"]

    def get_trips(self):
        return self.data["journeys"]

    def get_legs(self):
        return self.data["legs"]

    def get_vehjourneys(self):
        return self.data["vehjourneys"]

    def get_boarding_alighting(self):
        return self.data["stops"]

    def get_stops(self):
        return self.get_boarding_alighting()

    def get_ea(self):
        return self.get_boarding_alighting()

    def get_linkvolumes(self):
        return self.data["linkvolumes"]

    def get_planelements(self):
        return self.data["planelements"]

    def get_stop_points(self):
        return self.data["stop_points"]

    def load_stop_points(self):
        self.data["stop_points"] = analyse.data.get_stops(self.path)

    def load_data(self, with_stop_points=False):
        logging.info("Laoding Data for %s" % self.name)
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
        for name in keys:
            try:
                sep = keys[name]["sep"]
                path = os.path.join(self.path, keys[name]["path"])
                self.data[name] = pd.DataFrame.from_csv(path, sep=sep, encoding="utf-8").reset_index()
            except Exception as e:
                logging.error(e.message)
        if with_stop_points:
            self.load_stop_points()


class RunsDatabase:
    def __init__(self, path):
        self.path = path
        self.runs = defaultdict(dict)
        self.db = None
        self.rescan()

    def rescan(self):
        db = pd.read_csv(self.path)
        db.set_index(["Name"], inplace=True)
        self.db = db

    def get_names(self):
        return self.db.index

    def get_paths(self, names):
        return [self.get_path(k) for k in names]

    def get_path(self, name):
        return self.runs[name].path

    def add_run(self, name, path, scale_factor, overwrite=False):
        if not overwrite and name in self.db.index:
            logging.info("Name %s already in csv. Overwrite?" % name)
            return
        run = Run(name=name, path=path, scale_factor=scale_factor)

        self.runs[name] = run
        return run

    def load_run(self, name, with_stop_points):
        run = Run(name=name, path=self.db.loc[name].Path, scale_factor=self.db.loc[name].Factor)
        run.load_data(with_stop_points)
        self.runs[run.name] = run

    def load_data(self, only_new=True, names=None, with_stop_points=False):
        if names is None:
            names = self.db.index
        for name in names:
            if only_new:
                if name not in self.runs:
                    self.load_run(name, with_stop_points)
            else:
                self.load_run(name, with_stop_points)

    def get(self, sim_name):
        return self.runs[sim_name]

