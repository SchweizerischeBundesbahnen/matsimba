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

    def get_pt_run(self):
        teilwege = pd.read_csv(self.path_pt_legs, sep=";",
                          skiprows=12)

        teilwege.rename(columns={"$OEVTEILWEG:QBEZNR": "QBEZNR",
                                 "PFAHRT": PF,
                                 "ZEIT": "duration",
                                 "ABFAHRT": "start_time",
                                 "ANKUNFT": "end_time",
                                 "WEITE": "distance",
                                 "STARTFZPELEM\LINIENROUTENELEMENT\HALTEPUNKT\CODE": "START_CODE",
                                 "ENDFZPELEM\LINIENROUTENELEMENT\HALTEPUNKT\CODE": "END_CODE"
                                 }, inplace=True)

        teilwege = teilwege[teilwege.VONHPUNKTNR.notnull()]
        teilwege[trip_id] = teilwege.QBEZNR.map(str)+"_"+teilwege.ZBEZNR.map(str)+"_"+teilwege.WEGIND.map(str)
        teilwege[leg_id] = teilwege[trip_id]+"_"+teilwege.TWEGIND.map(str)

        teilwege["boarding_stop"] = teilwege.VONHPUNKTNR.map(int).map(str) + "_" + teilwege.START_CODE
        teilwege["alighting_stop"] = teilwege.NACHHPUNKTNR.map(int).map(str) + "_" + teilwege.END_CODE
        teilwege[PKM] = teilwege[PF]*teilwege.distance
        teilwege["mode"] = "pt"
        teilwege[SUBPOPULATION] = self.subpopulation

        pt_run = analyse.run.Run(name="FQKal+")
        pt_run.data["legs"] = teilwege
        return pt_run

    def get_count_stations(self):
        ref_astra = pd.read_csv(self.path_astra, sep=";", dtype={"link_id": str})
        ref_astra.rename(columns={"zaehlstellen_bezeichnung": "name"}, inplace=True)
        return ref_astra[ref_astra.name.isin(self.count_stations)]

    def get_count_stations_volume(self):
        df = self.get_count_stations().groupby("name").sum()[["volume"]] / 2.0
        return df.rename(columns={"volume": "ASTRA"})

