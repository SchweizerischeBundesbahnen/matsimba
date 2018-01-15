import pandas as pd
from variable import *
import analyse.run

path_count_linkvolumes = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/link_count_data_astra15.csv"
path_mikro = r"/opt/sbb/hdd/u222223/MATSim/mikrozensus/2015/20171212_Input_MZMV_Kalibrationsvergleich.csv"
path_count_ea = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/stop_count_data_fqkal+14_alles.csv"


class Reference:
    def __init__(self, path_astra, path_mikro, path_pt_legs, is_cnb=True):
        self.is_cnb = is_cnb
        self.subpopulation = "regular"
        if is_cnb:
            self.subpopulation = "regular_inAct"

        self.path_astra = path_astra
        self.path_mikro = path_mikro
        self.path_pt_legs = path_pt_legs

        self.stations = ["ZUE", "ZMUS", "BN", "W", "ZOER", "BS", "ZSTH", "GE", "LS", "SIO"]
        self.count_stations = ['WALLISELLEN (AB)',
                               'MUTTENZ, HARD (AB)',
                               'BADEN, BAREGGTUNNEL (AB)',
                               'NEUENHOF (AB) - AG1402',
                               'WUERENLOS (AB) - AG1401',
                               'CRISSIER (AR)',
                               'BERN, FELSENAUVIADUKT (AB)',
                               'RENENS (AR)',
                               'UMF. ZUERICH N, AFFOLTERN (AB)',
                               'LUZERN, REUSSPORTTUNNEL (AB)',
                               'PREVERENGES (AR)',
                               'CONT. DE LAUSANNE (AR)',
                               'GUNZGEN (AB)',
                               'WINTERTHUR TOESS (AB) - ZH105',
                               'CHAM N (AB)',
                               'LAUSANNE BLECHERETTE (AR)',
                               'NIEDERBIPP (AB)',
                               'DEITINGEN (AB)',
                               'URDORF (AB)',
                               'EMMENBRUECKE, GRUEBLISCH. (AB)']

    def get_mzmv_run(self):
        df = pd.read_csv(self.path_mikro, sep=",", dtype={"link_id": str})
        df[SUBPOPULATION] = self.subpopulation
        df = df.rename(columns={u'Weglaenge': "distance"})
        df = df.rename(columns={u'Pkm': "PKM"})
        df.distance = df.distance * 1000.0

        if self.is_cnb:
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

    def get_count_stations_volume(self):
        df = self.get_count_stations().groupby("name").sum()[["volume"]]/2.0
        return df.rename(columns={"volume": "ASTRA"})