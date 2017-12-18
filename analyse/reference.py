import pandas as pd
from variable import *
import analyse.run

path_count_linkvolumes = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/link_count_data_astra15.csv"
path_mikro = r"/opt/sbb/hdd/u222223/MATSim/mikrozensus/2015/20171212_Input_MZMV_Kalibrationsvergleich.csv"
path_count_ea = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/stop_count_data_fqkal+14_alles.csv"


class Reference:
    def __init__(self, path_astra, path_mikro, path_ea):
        self.path_astra = path_astra
        self.path_mikro = path_mikro
        self.path_ea = path_ea

        self.stations = ["BI", "NE", "CF", "SCB", "LOC", "STI"]
        self.count_stations = ['HAUTERIVE (AR)',
                               'ST-URSANNE, TUN. TERRI (AR)',
                               'DEVELIER (AR)',
                               'WALLISELLEN (AB)',
                               'ROTHENBURG (AB)',
                               'VAUMARCUS (AR)',
                               'ROTHENBRUNNEN S (AB)',
                               'MATTSTETTEN (AB)',
                               'ROLLE N (AR)',
                               'NYON, CRASSIER (AR)']

    def get_mzmv_run(self, subpopulation="regular_inAct", is_cnb=False):
        df = pd.read_csv(self.path_mikro, sep=",", dtype={"link_id": str})
        df[SUBPOPULATION] = subpopulation
        df = df.rename(columns={u'Weglaenge': "distance"})
        df = df.rename(columns={u'Pkm': "PKM"})
        df.distance = df.distance * 1000.0

        if is_cnb:
            df = pd.DataFrame(df[df.istCNB])
        mzmv = analyse.run.Run(name="mzmv")
        mzmv.data["journeys"] = df
        return mzmv

    def get_stations(self):
        ref_ea = pd.read_csv(self.path_ea, sep=";")
        ref_ea[CODE] = ref_ea.stop_id.apply(lambda x: x.split("_")[-1])

        ref_ea = ref_ea.groupby(CODE)[["boarding"]].sum()
        ref_ea = ref_ea.rename(columns={"boarding": "FQKal+"})
        return ref_ea.loc[self.stations]

    def get_count_stations(self):
        ref_astra = pd.read_csv(self.path_astra, sep=";", dtype={"link_id": str})
        ref_astra.rename(columns={"zaehlstellen_bezeichnung": "name"}, inplace=True)
        return ref_astra[ref_astra.name.isin(self.count_stations)]
