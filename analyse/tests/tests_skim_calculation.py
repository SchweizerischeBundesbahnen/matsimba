#!/usr/bin/env python
# -*- coding: cp1252-*-
import os
import unittest

import pandas as pd

from analyse.skims import filter_legs_to_binnenverkehr_fq_legs, prepare_oevteilwege_visum, \
    get_station_to_station_skims


class MyTestCase(unittest.TestCase):
    def test_skims_for_visum_teilwege(self):
        path_data = os.path.join("..", "..", "data_in", "test")

        path_oev_teilwege_visum = os.path.join(path_data, "oev_teilwege_visum.att")
        path_stop_ids_cnb = os.path.join(path_data, "stop_id_in_cnb.csv")
        path_stop_ids_cnb_normalspur = os.path.join(path_data, "stop_id_in_cnb_normalspur.csv")

        df_oevteilwege_visum = pd.read_csv(path_oev_teilwege_visum, sep="\t", skiprows=12, encoding='cp1252')
        stop_ids_cnb = set(pd.read_csv(path_stop_ids_cnb, sep=";")["stop_id"].unique())
        stop_ids_cnb_normalspur = set(pd.read_csv(path_stop_ids_cnb_normalspur, sep=";")["stop_id"].unique())

        df_oevteilwege_visum_prepared = prepare_oevteilwege_visum(df_oevteilwege_visum)

        fq_legs_visum = filter_legs_to_binnenverkehr_fq_legs(df_oevteilwege_visum_prepared, stop_ids_cnb,
                                                             stop_ids_cnb_normalspur, from_simba_visum=True)

        skims_visum = get_station_to_station_skims(fq_legs_visum, from_simba_visum=True)
        skims_bv_nese = skims_visum[
            (skims_visum["first_stop"] == "1422_BV") & (skims_visum["last_stop"] == "2346_NESE")]

        self.assertEquals(skims_bv_nese["bz_hhmmss"].iloc[0], "00:12:04", msg="trip over midnight!")
        self.assertAlmostEqual(skims_bv_nese["uh"].iloc[0], 0.048857476, places=5, msg="umsteigehäufigkeit")
        self.assertAlmostEqual(skims_bv_nese["distance"].iloc[0], 10.11100000, places=5, msg="distanz")
        self.assertAlmostEqual(skims_bv_nese["PFAHRT"].iloc[0], 14.573, places=5, msg="pf")

    def test_skims_for_matsim_legs(self):
        path_data = os.path.join("..", "..", "data_in", "test")

        path_trips_matsim = os.path.join(path_data, "matsim_trips_for_skimtest.txt")
        path_stop_ids_cnb = os.path.join(path_data, "stop_id_in_cnb.csv")
        path_stop_ids_cnb_normalspur = os.path.join(path_data, "stop_id_in_cnb_normalspur.csv")

        df_trips_matsim = pd.read_csv(path_trips_matsim, sep="\t")
        stop_ids_cnb = set(pd.read_csv(path_stop_ids_cnb, sep=";")["stop_id"].unique())
        stop_ids_cnb_normalspur = set(pd.read_csv(path_stop_ids_cnb_normalspur, sep=";")["stop_id"].unique())

        fq_legs_matsim = filter_legs_to_binnenverkehr_fq_legs(df_trips_matsim, stop_ids_cnb,
                                                              stop_ids_cnb_normalspur)

        skims_matsim = get_station_to_station_skims(fq_legs_matsim, factor=10.0)
        skims_bi_ins = skims_matsim[
            (skims_matsim["first_stop"] == "1279_BI") & (skims_matsim["last_stop"] == "1984_INS")]

        self.assertEquals(skims_bi_ins["bz_hhmmss"].iloc[0], "00:32:02", msg="trip over midnight!")
        self.assertAlmostEqual(skims_bi_ins["uh"].iloc[0], 1.0, places=5, msg="umsteigehäufigkeit")
        self.assertAlmostEqual(skims_bi_ins["distance"].iloc[0], 42.345000, places=5, msg="distanz")
        self.assertAlmostEqual(skims_bi_ins["PFAHRT"].iloc[0], 30.0, places=5, msg="pf")


if __name__ == '__main__':
    unittest.main()
