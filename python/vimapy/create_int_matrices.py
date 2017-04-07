#!/usr/bin/env python
# -*- coding: cp1252-*-
import logging

import win32com.client
import numpy as np
import random
import math

def randomround(value, precision):
    """
    Die Funktion rundet den Eingabewert zufällig auf n Stellen nach dem Komma
    Zufällig Runden einer Zahl x heisst folgendes: Sei x_minus die auf n Stellen abgerundete Zahl von x
    und x_plus die auf n Stellen aufgerundete Zahl von x. x wird nun mit Wahrscheinlichkeit
    p=1-(x-x_minus)/(x_plus-x_minus) auf x_minus und mit Wahrscheinlichkeit p auf x_plus gerundet.
    '21.09.2010 JL => von VBA nach Python übertragen am 07.04.17
    """
    x_minus = float(math.floor(value * (10.0 ** precision))) / (10.0 ** precision)
    x_plus = float(math.ceil(value * (10.0 ** precision))) / (10.0 ** precision)
    random_number = random.random()
    if (random_number < (value - x_minus) / (10.0 ** -precision)):
        return x_plus
    else:
        return x_minus

def main(path_visumversion_in, path_visumversion_out):
    logging.basicConfig(level=logging.INFO,
                        filename='',  # log to this file
                        format='%(asctime)s %(message)s')
    logging.info("start")
    visum = win32com.client.Dispatch("Visum.Visum.150")
    visum.LoadVersion(path_visumversion_in)
    logging.info("visum-version geladen")
    for matrix_nr in range(1, 145):
        matrix = visum.Net.Matrices.ItemByKey(matrix_nr)
        values = np.array(matrix.GetValues())
        nb_zones = len(values)
        logging.info("start matrix {}".format(matrix_nr))
        for i in range(nb_zones):
            for j in range(nb_zones):
                value = values[i, j]
                if value > 0.0:
                    values[i, j] = randomround(values[i, j], 0)
        matrix.SetValues(values)
    # Visum.Procedures.Execute()
    visum.SaveVersion(path_visumversion_out)



if __name__ == "__main__":
    # n = 0
    # for i in range(100000):
    #     n += randomround(0.001, 0)
    # print n
    # print randomround(1.1, 0)
    # print randomround(0.9, 0)
    # print randomround(725.5, 0)
    # print randomround(10004.001, 0)
    # print randomround(0.999, 0)
    path_visumversion_in = r"\\V00925\80_MATSim\14_senozon_RailFit\30_validierung_oev_umlegung\01_Visum_Versionen\REF_STEP2030_M_mPM_mCeva_UML_DWV_01_UeL_BAV_v05.ver"
    path_visumversion_out = r"\\V00925\80_MATSim\14_senozon_RailFit\30_validierung_oev_umlegung\01_Visum_Versionen\REF_STEP2030_M_mPM_mCeva_UML_DWV_01_UeL_BAV_v05_intMatrix.ver"
    main(path_visumversion_in, path_visumversion_out)

