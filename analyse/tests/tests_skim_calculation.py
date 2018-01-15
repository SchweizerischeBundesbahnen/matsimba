#!/usr/bin/env python
# -*- coding: cp1252-*-
import os
import unittest

import pandas as pd

from analyse.skims import filter_legs_to_binnenverkehr_fq_legs, prepare_oevteilwege_visum, \
    get_station_to_station_skims, read_stops_in_perimeter, read_fqrelevant_stops, read_oev_teilwege_visum, \
    read_matsim_trips


class MyTestCase(unittest.TestCase):

    def test_read_att_file(self):
        path_data = os.path.join("..", "..", "data_in", "test")
        path_att_file = os.path.join(path_data, "20180109_PerimeterSimbaBahn_Attribute.att")

        # stops in CH-perimeter
        stops_in_perimeter_ch = read_stops_in_perimeter(path_att_file, "ISTSIMBABAHNCHPERIMETER")
        self.assertEquals(len(stops_in_perimeter_ch), 1955, msg="nb of stops in ch-perimeter")

        # stops in CNB-perimeter
        stops_in_perimeter_cnb = read_stops_in_perimeter(path_att_file, "ISTSIMBABAHNCNBPERIMETER")
        self.assertEquals(len(stops_in_perimeter_cnb), 127, msg="nb of stops in cnb-perimeter")

        # fq-relevant stops
        stops_fq_relevant = read_fqrelevant_stops(path_att_file)
        self.assertEquals(len(stops_fq_relevant), 1367, msg="nb of fq-relevant stops")

    def test_skims_for_visum_teilwege(self):
        path_data = os.path.join("..", "..", "data_in", "test")

        path_oev_teilwege_visum = os.path.join(path_data, "oev_teilwege_visum.att")
        path_att_file = os.path.join(path_data, "20180109_PerimeterSimbaBahn_Attribute.att")

        stop_ids_cnb = read_stops_in_perimeter(path_att_file, "ISTSIMBABAHNCNBPERIMETER")
        stops_ids_fq_relevant = read_fqrelevant_stops(path_att_file)

        df_oevteilwege_visum_prepared = read_oev_teilwege_visum(path_oev_teilwege_visum)

        fq_legs_visum = filter_legs_to_binnenverkehr_fq_legs(df_oevteilwege_visum_prepared, stop_ids_cnb,
                                                             stops_ids_fq_relevant, from_simba_visum=True)

        skims_visum = get_station_to_station_skims(fq_legs_visum, from_simba_visum=True)
        skims_bv_nese = skims_visum[
            (skims_visum["first_stop"] == '1422') & (skims_visum["last_stop"] == '2346')]

        self.assertEquals(skims_bv_nese["bz_hhmmss"].iloc[0], "00:12:04", msg="trip over midnight!")
        self.assertAlmostEqual(skims_bv_nese["uh"].iloc[0], 0.048857476, places=5, msg="umsteigehäufigkeit")
        self.assertAlmostEqual(skims_bv_nese["distance"].iloc[0], 10.11100000, places=5, msg="distanz")
        self.assertAlmostEqual(skims_bv_nese["PFAHRT"].iloc[0], 14.573, places=5, msg="pf")

    def test_skims_for_matsim_legs(self):
        path_data = os.path.join("..", "..", "data_in", "test")

        path_trips_matsim = os.path.join(path_data, "matsim_trips_for_skimtest.txt")

        path_att_file = os.path.join(path_data, "20180109_PerimeterSimbaBahn_Attribute.att")

        stop_ids_cnb = read_stops_in_perimeter(path_att_file, "ISTSIMBABAHNCNBPERIMETER")
        stops_ids_fq_relevant = read_fqrelevant_stops(path_att_file)

        df_trips_matsim = read_matsim_trips(path_trips_matsim)

        fq_legs_matsim = filter_legs_to_binnenverkehr_fq_legs(df_trips_matsim, stop_ids_cnb,
                                                              stops_ids_fq_relevant)

        skims_matsim = get_station_to_station_skims(fq_legs_matsim, factor=10.0)
        skims_bi_ins = skims_matsim[
            (skims_matsim["first_stop"] == '1279') & (skims_matsim["last_stop"] == '1984')]

        self.assertEquals(skims_bi_ins["bz_hhmmss"].iloc[0], "00:32:02", msg="trip over midnight!")
        self.assertAlmostEqual(skims_bi_ins["uh"].iloc[0], 1.0, places=5, msg="umsteigehäufigkeit")
        self.assertAlmostEqual(skims_bi_ins["distance"].iloc[0], 42.345000, places=5, msg="distanz")
        self.assertAlmostEqual(skims_bi_ins["PFAHRT"].iloc[0], 30.0, places=5, msg="pf")

    def test_full_cnb_matsim_trips(self):

        path_data = os.path.join("..", "..", "data_in", "test")
        path_trips_matsim = os.path.join(path_data, "matsim_trips_full_cnb.txt")
        path_att_file = os.path.join(path_data, "20180109_PerimeterSimbaBahn_Attribute.att")

        df_trips = pd.read_csv(path_trips_matsim, sep="\t")
        stop_ids_cnb = read_stops_in_perimeter(path_att_file, "ISTSIMBABAHNCNBPERIMETER")
        stops_ids_fq_relevant = read_fqrelevant_stops(path_att_file)
        fq_legs_matsim = filter_legs_to_binnenverkehr_fq_legs(df_trips, stop_ids_cnb, stops_ids_fq_relevant)
        self.assertEquals(len(fq_legs_matsim) > 0, True, msg="non empty")


if __name__ == '__main__':
    unittest.main()
