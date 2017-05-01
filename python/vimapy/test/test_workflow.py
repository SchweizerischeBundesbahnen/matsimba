import unittest
import ConfigParser
import os
import python_path
python_path.load()
import vipy.visum
import put_supply
import demand
import importer

config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.ini")
config.read(config_path)

output_path = os.path.abspath("../../data_out")


class TestDelete(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v = vipy.visum.Visum()
        v.lade_version(os.path.abspath(config.get("VisumVersions", "small")))
        cls.v = v

    @classmethod
    def tearDownClass(cls):
        cls.v.close()

    def test_export(self):
        put_supply.set_projection(self.v, config)
        put_supply.export(self.v, folder=output_path, config=config)
        demand.export(self.v, os.path.join(output_path, "population.xml"))

    @unittest.skip("need leuk licencse")
    def test_import(self):
        #path_trips =
        #path_output =
        #importer.import_trips_in_visum(self.v, )
        pass