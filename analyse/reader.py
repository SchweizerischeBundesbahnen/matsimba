import glob
import os
import pandas as pd
import gzip
import xml.etree.ElementTree as ET
import logging


def get_stops(folder):
    transitfiles = glob.glob(os.path.join(folder, "*transitSchedule.xml.gz"))
    if len(transitfiles)==0:
        logging.warn("No transitSchedule.xml.gz found")
        return None
    
    with gzip.open(transitfiles[0], 'rb') as f:
        file_content = f.read()
        tree = ET.fromstring(file_content)

        stops = []
        for a in tree.findall("transitStops"):
            for stop in a.findall("stopFacility"):
                stops.append(stop.attrib)

        return pd.DataFrame.from_dict(stops)


def get_persons_from_xml(folder, attributes_file=None, persons_file=None):
    if attributes_file is None:
        attributes_file = glob.glob(os.path.join(folder, "*Attributes.xml.gz"))[0]
    with gzip.open(attributes_file, 'rb') as f:
        file_content = f.read()
        tree_attributes = ET.fromstring(file_content)

        attributes_dict = {}
        for d in tree_attributes.findall("object"):
            _id = d.attrib["id"]
            attributes_dict[_id] = {}
            for dd in d.findall("attribute"):
                attributes_dict[_id][dd.attrib["name"]] = dd.text

        if persons_file is None:
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



