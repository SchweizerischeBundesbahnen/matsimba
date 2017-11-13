#!/usr/bin/env python
# -*- coding: cp1252-*-
import os


def schreibe_erste_zeilen(folder_in, folder_out, anz_zeilen):

    with open(os.path.join(folder_in, 'matsim_trips.txt')) as trips_file, \
            open(os.path.join(folder_out, 'matsim_trips.txt'), "w") as trips_file_out:
        i = 0
        for line in trips_file:
            if i < anz_zeilen:
                trips_file_out.write(line)
                i += 1


def get_csv_line(l):
    return ";".join([str(x) for x in l]) + "\n"


if __name__ == "__main__":
    folder_in = r"\\V00925\80_MatSim\14_senozon_RailFit\30_validierung_oev_umlegung\01_Visum_Versionen\AnalyseZufRunden"
    folder_out = r"..\..\data_in\test"
    schreibe_erste_zeilen(folder_in, folder_out, 100)


def hhmmss_to_seconds(hhmmss):
    h, m, s = tuple([int(x) for x in hhmmss.split(":")])
    return h*60*60 + m*60 + s


def seconds_to_hhmmss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)