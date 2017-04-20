import os
import unittest

from python.vimapy.importer import import_trips_in_visum


class TestTripImportVisum(unittest.TestCase):
    def test_verfahren(self):
        folder_in = r"..\..\data_in\test"
        folder_out = r"..\..\data_out\test"
        path_trips_file = os.path.join(folder_in, 'matsim_trips.txt')
        path_visum_version = r"\\V00925\80_MatSim\30_TopDown\visum\REF_STEP2030_M_mPM_mCeva_UML_DWV_01_UeL_BAV_v05_intMatrix.ver"
        path_out_trips_for_visum = os.path.join(folder_out, 'matsim_trips_for_visum.csv')
        import_trips_in_visum(path_trips_file, path_visum_version, path_out_trips_for_visum)

if __name__ == '__main__':
    unittest.main()