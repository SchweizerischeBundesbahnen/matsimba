import pandas as pd
from variable import *
import analyse.run

path_count_linkvolumes = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/link_count_data_astra15.csv"
path_mikro = r"/opt/sbb/hdd/u222223/MATSim/mikrozensus/2015/20171212_Input_MZMV_Kalibrationsvergleich.csv"
path_count_ea = r"/opt/sbb/hdd/u222223/MATSim/simulations/CH/zaehldaten/stop_count_data_fqkal+14_alles.csv"
import math

class Reference:
    pt_run = None
    mzmv_run = None

    def __init__(self, path_astra, path_mikro, path_pt_legs, is_cnb=True, pt_run_name="SIMBA.Bahn.16"):
        self.is_cnb = is_cnb
        self.subpopulation = "regular"
        if is_cnb:
            self.subpopulation = "regular_inAct"

        self.path_astra = path_astra
        self.path_mikro = path_mikro
        self.path_pt_legs = path_pt_legs

        self.stations = ['ZUE', 'BN', 'W', 'ZOER', 'BS', 'ZSTH', 'GE', 'LS', 'LZ', "OL", "ZHDB", "BI"]
        self.tsys_names = ['GB', 'LB', 'FUN', 'BUS', 'NFB', 'NFO', 'KB', 'M', 'NFT', 'T',
                           'FV-RV - ProduktC', 'RV - ProduktD', 'IPV - Regionalverkehr',
                           'FV - ProduktA', 'FV - ProduktB', 'IPV - HGV',
                           'IPV - Konventionell', 'BAT', 'FAE']

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

        self.operators = ["SBB-FV", "SBB-RV", r"Thurbo", r"Lyria", "Region Alps"]

        self.load_mzmv_run()
        self.load_pt_run(pt_run_name)

    def load_mzmv_run(self):
        df = pd.read_csv(self.path_mikro, sep=",", dtype={"link_id": str})
        df[SUBPOPULATION] = self.subpopulation
        df = df.rename(columns={u'Weglaenge': "distance"})
        df = df.rename(columns={u'Pkm': "PKM"})
        df.distance = df.distance * 1000.0

        if self.is_cnb:
            df = pd.DataFrame(df[df.istCNB])
        mzmv = analyse.run.Run(name="mzmv")
        mzmv.data["journeys"] = df
        self.mzmv = mzmv

    def get_mzmv_run(self):
        return self.mzmv

    def load_pt_run(self, name):
        teilwege = pd.read_csv(self.path_pt_legs, sep=";",
                               skiprows=12)

        teilwege.rename(columns={"$OEVTEILWEG:QBEZNR": "QBEZNR",
                                 "PFAHRT": PF,
                                 "ZEIT": "duration",
                                 "ABFAHRT": "start_time",
                                 "ANKUNFT": "end_time",
                                 "WEITE": "distance",
                                 "VONHPUNKTNR": "boarding_stop",
                                 "NACHHPUNKTNR": "alighting_stop",
                                 r"OEVVSYS\NAME": r"08_TSysName",
                                 "FAHRZEITPROFIL\LINIENROUTE\LINIE\BETREIBER\NAME": "06_OperatorName",
                                 "STARTFZPELEM\LINIENROUTENELEMENT\HALTEPUNKT\HALTESTELLENBEREICH\HALTESTELLE\CODE": "03_Stop_Code_boarding",
                                 "ENDFZPELEM\LINIENROUTENELEMENT\HALTEPUNKT\HALTESTELLENBEREICH\HALTESTELLE\CODE": "03_Stop_Code_alighting"
                                 }, inplace=True)

        teilwege = teilwege[teilwege.boarding_stop.notnull()]

        digits_z = int(math.log10(teilwege.ZBEZNR.max())) + 1
        digits_i = int(math.log10(teilwege.WEGIND.max())) + 1

        def to_int(q, z, i):
            return q * 10 ** (digits_i + digits_z) + z * 10 ** (digits_i) + i

        a = teilwege.QBEZNR.apply(lambda x: to_int(x, 0, 0))
        b = teilwege.ZBEZNR.apply(lambda x: to_int(0, x, 0))
        c = teilwege.WEGIND.apply(lambda x: to_int(0, 0, x))
        teilwege[trip_id] = a + b + c

        teilwege[leg_id] = teilwege[trip_id].map(str) + "_" + teilwege.TWEGIND.map(str)

        teilwege[PKM] = teilwege[PF] * teilwege.distance
        teilwege["mode"] = "pt"
        teilwege[IS_SIMBA] = True
        teilwege[SUBPOPULATION] = self.subpopulation

        pt_run = analyse.run.Run(name=name)
        pt_run.data["legs"] = teilwege
        self.pt_run = pt_run
        analyse.run.Run._create_starttime_class(self.pt_run.get_legs())

    def get_pt_run(self):
        return self.pt_run

    def get_count_stations(self):
        ref_astra = pd.read_csv(self.path_astra, sep=";", dtype={"link_id": str})
        ref_astra.rename(columns={"zaehlstellen_bezeichnung": "name"}, inplace=True)
        return ref_astra[ref_astra.name.isin(self.count_stations)]

    def get_count_stations_volume(self):
        df = self.get_count_stations().groupby("name").sum()[["volume"]] / 2.0
        return df.rename(columns={"volume": "ASTRA"})
