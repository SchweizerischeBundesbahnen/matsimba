import pandas as pd
from collections import defaultdict
import os


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

    def load_data(self, only_new=True, names=None):
        if names is not None:
            names = self.db.index
        for name in names:
            if only_new:
                if name not in self.data:
                    self._load_data(name)
            else:
                self._load_data(name)

    def _load_data(self, run_name):

        keys = {"acts": {"path": "matsim_activities.txt", "sep": "\t"},
                "journeys": {"path": "matsim_journeys.txt", "sep": "\t"},
                "legs": {"path": "matsim_trips.txt", "sep": "\t"},
                "vehjourneys": {"path": "matsim_vehjourneys.csv", "sep": ";"},
                "stops": {"path": "matsim_stops.csv", "sep": ";"},
                "linkvolumes": {"path": "matsim_linkvolumes.csv", "sep": ";"},
                "planelements": {"path": "plan_elements.csv", "sep": ";"},
                "persons": {"path": "agents.csv", "sep": ";"}}
        _path = self.get_path(run_name)
        for name in keys:
            try:
                sep = keys[name]["sep"]
                path = os.path.join(_path, keys[name]["path"])
                self.data[run_name][name] = pd.DataFrame.from_csv(path, sep=sep, encoding="utf-8").reset_index()
            except Exception as e:
                print e.message

