import pandas as pd
import io
from PIL import Image
from variable import *


class SheetData:
    def __init__(self, df, fig, name):
        self.df = df
        self.fig = fig
        self.name = name


def make_report(runs, filename, ref=None, is_cnb=True, subpopulation="regular"):
    datas = get_datas(runs=runs, ref=ref, is_cnb=is_cnb, subpopulation=subpopulation)
    _make_report(datas=datas, filename=filename)


def _make_report(datas, filename):
    buffers = []

    def get_buffer(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        buffers.append(buf)
        return buf

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    worksheet = writer.book.add_worksheet("TableOfContents")
    for i, data in enumerate(datas):
        worksheet.write_url(i + 1, 1, url="internal:'%s'!A1" % data.name, string=data.name)

    for data in datas:
        df = data.df
        buf = get_buffer(data.fig)
        sheet = writer.book.add_worksheet(data.name)
        sheet.insert_image('A1', "aa", {'image_data': buf})
        df.to_excel(writer, sheet_name=data.name + "_data", startrow=1, startcol=1)

    writer.save()

    for buf in buffers:
        buf.close()


def get_datas(runs, ref, is_cnb=False, subpopulation="regular"):
    datas = []

    mzmv = ref.mzmv = ref.get_mzmv_run(is_cnb=is_cnb, subpopulation=subpopulation)

    df, ax = runs.plot_nb_trips(by=MAIN_MODE, foreach=SUBPOPULATION, ref_run=mzmv, percent=True)
    datas.append(SheetData(df, ax, "#trips 1"))

    df, ax = runs.plot_nb_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, SEASON_TICKET], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, ax, "#trips 2"))

    df, fig = runs.plot_nb_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, RAUMTYP], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, fig, "#trips 3"))

    df, fig = runs.plot_nb_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, CARAVAIL], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, fig, "#trips 4"))

    df, ax = runs.plot_pkm_trips(by=MAIN_MODE, foreach=SUBPOPULATION, ref_run=mzmv, percent=True)
    datas.append(SheetData(df, ax, "pkm trips 1"))

    df, ax = runs.plot_pkm_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, SEASON_TICKET], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, ax, "pkm trips 2"))

    df, fig = runs.plot_pkm_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, RAUMTYP], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, fig, "pkm trips 3"))

    df, fig = runs.plot_pkm_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, CARAVAIL], ref_run=mzmv, percent=True)
    datas.append(SheetData(df, fig, "pkm trips 4"))

    df, fig = runs.plot_pkm_distr_trips(foreach=[MAIN_MODE], percent=True, rotate=True, ref_run=mzmv)
    datas.append(SheetData(df, fig, "pkm distribution"))

    df, fig = runs.plot_pkm_distr_trips(foreach=[MAIN_MODE, SUBPOPULATION, SEASON_TICKET], percent=True,
                                        rotate=True, ref_run=mzmv, inverse_percent_axis=True,
                                        percent_level=["subpopulation"])
    datas.append(SheetData(df, fig, "pkm distribution 2"))

    df, fig = runs.plot_pkm_distr_legs(foreach=[IS_SIMBA_FQ], percent=True, inverse_percent_axis=True,
                                       rotate=True)
    datas.append(SheetData(df, fig, "simba_legs"))

    df, fig = runs.plot_einsteiger(by=CODE, codes=ref.get_stations().index.tolist(), ref_df=ref.get_stations())
    datas.append(SheetData(df, fig, "Einsteiger"))

    df, fig = runs.plot_einsteiger(by=CODE, codes=ref.get_stations().index.tolist(),
                                   foreach=[SUBPOPULATION, SEASON_TICKET])
    datas.append(SheetData(df, fig, "Einsteiger 2"))

    df, fig = runs.plot_vehicles(by="name", names=ref.get_count_stations().name.unique().tolist(),
                                 ref_df=ref.get_count_stations_volume())
    datas.append(SheetData(df, fig, "Link counts"))

    return datas
