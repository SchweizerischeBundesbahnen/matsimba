#!/usr/bin/env python
# -*- coding: cp1252-*-
import csv
import logging
import os

import sys

import vipy
import vipy.visum


sys.path.append(r"C:\Program Files\PTV Vision\PTV Visum 16\Exe\PythonModules")
from VisumPy.helpers import secs2HHMMSS

from python.vimapy.helpers import get_csv_line


def import_trips_in_visum(path_trips_file, path_visum_version, path_out_trips_for_visum):
    logging.basicConfig(level=logging.INFO,
                        filename='',  # log to this file
                        format='%(asctime)s %(message)s')
    logging.info("pfad trips-file: {}".format(path_trips_file))
    logging.info("pfad visum-version: {}".format(path_visum_version))
    logging.info("pfad trips-file-for-visum-out: {}".format(path_out_trips_for_visum))

    v = vipy.visum.Visum()
    v.lade_version(path_visum_version)
    logging.info("visum-version geöffnet")
    fzps = v.apl.hole_fahrzeitprofile()
    fzp_pro_id = {}
    for fzp in fzps:
        id = int(fzp.nummer())
        fzp_pro_id[id] = fzp
    logging.info("fzp verarbeitet. anz fzp: {}".format(len(fzp_pro_id)))
    hps = v.netz.hole_haltepunkte()
    hsnr_pro_hpnr = {}
    for hp in hps:
        hpnr = int(hp.nummer())
        hsnr = int(vipy.angebot.helper.hole_setze_attribut(hp.com_objekt, "STOPAREA\STOP\NO"))
        hsnr_pro_hpnr[hpnr] = hsnr
    logging.info("hp und hs verarbeitet. anz hps: {}".format(len(hsnr_pro_hpnr)))

    logging.info("start trips für visum schreiben")
    header = """
$VISION
* VisumInst
* 10.11.06
*
*
* Tabelle: Versionsblock
$VERSION:VERSNR;FILETYPE;LANGUAGE;UNIT
4.00;Att;DEU;KM
*
*
* Tabelle: ÖV-Teilwege\n
"""
    spaltennamen_list = ["$OEVTEILWEG:VONHSTNR",
                         "NACHHSTNR",
                         "DATENSATZNR",
                         "WEGIND",
                         "TWEGIND",
                         "PFAHRT",
                         "LinName",
                         "LinRouteName",
                         "RichtungCode",
                         "FZProfilName",
                         "EingabeHstAbfahrtstag",
                         "EingabeHstAbfahrtszeit",
                         "EingabeHStNr"]
    with open(path_trips_file) as trips_file, open(path_out_trips_for_visum, "w") as trips_for_visum:
        trips_for_visum.write(header)
        trips_for_visum.write(get_csv_line(spaltennamen_list))
        reader = csv.DictReader(trips_file, delimiter="\t")
        journey_id_old = None
        weg_index = 0
        for row in reader:
            journey_id = int(row["journey_id"])
            if journey_id != journey_id_old:
                weg_index += 1
                index = 1
            if row["mode"] == "pt":
                hpnr_von = int(row["boarding_stop"].split("_")[0])
                hsnr_von = hsnr_pro_hpnr[hpnr_von]
                hpnr_bis = int(row["alighting_stop"].split("_")[0])
                fzpid = int(row["route"].split("_")[0])
                fzp = fzp_pro_id[fzpid]
                l = [hsnr_von,
                     hsnr_pro_hpnr[hpnr_bis],
                     journey_id,
                     weg_index,
                     index,
                     1.0,
                     fzp.linename(),
                     fzp.lineroutename(),
                     fzp.richtung(),
                     fzp.name(),
                     1,
                     secs2HHMMSS(int(row["start_time"])),
                     hsnr_von]
                trips_for_visum.write(get_csv_line(l))
                index += 1
            journey_id_old = journey_id

    logging.info("trips gelesen und geschrieben")




if __name__ == "__main__":
    folder_in = r"..\..\data_in\test"
    folder_out = r"..\..\data_out\test"
    # path_trips_file = os.path.join(folder_in, 'matsim_trips.txt')
    path_trips_file = r"\\v00925\80_MatSim\14_senozon_RailFit\30_validierung_oev_umlegung\01_Visum_Versionen\AnalyseZufRunden\matsim_trips.txt"
    path_visum_version = r"\\v00925\80_MatSim\14_senozon_RailFit\30_validierung_oev_umlegung\01_Visum_Versionen\REF_STEP2030_M_mPM_mCeva_UML_DWV_01_UeL_BAV_v05_intMatrix.ver"
    path_out_trips_for_visum = os.path.join(folder_out, 'matsim_trips_for_visum.csv')
    import_trips_in_visum(path_trips_file, path_visum_version, path_out_trips_for_visum)