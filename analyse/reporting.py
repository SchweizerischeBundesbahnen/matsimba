import pandas as pd
import io
from PIL import Image
from variable import *


class SheetData:
    def __init__(self, df, fig, name):
        self.df = df
        self.fig = fig
        self.name = name


def make_report(runs, filename, ref=None):
    datas = get_datas(runs=runs, ref=ref)
    _make_report(datas=datas, filename=filename)


def _make_report(datas, filename):
    buffers = []

    def get_buffer(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        im = Image.open(buf)
        im.show()
        buffers.append(buf)
        return buf

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    worksheet = writer.book.add_worksheet("TableOfContents")
    for i, data in enumerate(datas):
        worksheet.write_url(i + 1, 1, url="internal:'%s'!A1" % data.name, string=data.name)

    for data in datas:
        df = data.df
        df.to_excel(writer, sheet_name=data.name, startrow=1, startcol=18)
        buf = get_buffer(data.fig)
        writer.sheets[data.name].insert_image('A1', "aa", {'image_data': buf})

    writer.save()

    for buf in buffers:
        buf.close()


def get_datas(runs, ref):
    datas = []

    df, ax = runs.plot_nb_trips(by=MAIN_MODE, foreach=SUBPOPULATION)
    datas.append(SheetData(df, ax, "#trips 1"))

    df, ax = runs.plot_nb_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, SEASON_TICKET])
    datas.append(SheetData(df, ax, "#trips 2"))

    df, fig = runs.plot_nb_trips(by=MAIN_MODE, foreach=[RAUMTYP, SUBPOPULATION])
    datas.append(SheetData(df, fig, "#trips 3"))

    df, ax = runs.plot_pkm_trips(by=MAIN_MODE, foreach=SUBPOPULATION)
    datas.append(SheetData(df, ax, "pkm trips 1"))

    df, ax = runs.plot_pkm_trips(by=MAIN_MODE, foreach=[SUBPOPULATION, SEASON_TICKET])
    datas.append(SheetData(df, ax, "pkm trips 2"))

    df, fig = runs.plot_pkm_trips(by=MAIN_MODE, foreach=[RAUMTYP, SUBPOPULATION])
    datas.append(SheetData(df, fig, "pkm trips 3"))

    df, fig = runs.plot_pkm_distr_trips(foreach=[MAIN_MODE], percent=True, rotate=True)
    datas.append(SheetData(df, fig, "pkm distribution"))

    df, fig = runs.plot_pkm_distr_trips(foreach=[MAIN_MODE, SUBPOPULATION, SEASON_TICKET], percent=True,
                                        rotate=True)
    datas.append(SheetData(df, fig, "pkm distribution 2"))

    df, fig = runs.plot_pkm_distr_legs(foreach=[IS_SIMBA_FQ], percent=True, inverse_percent_axis=False, rotate=True)
    datas.append(SheetData(df, fig, "simba_legs"))

    df, fig = runs.plot_einsteiger(by=CODE, codes=ref.get_stations().index, ref_df=ref.get_stations())
    datas.append(SheetData(df, fig, "Einsteiger"))

    df, fig = runs.plot_einsteiger(by=CODE, codes=ref.get_stations().index, foreach=SUBPOPULATION)
    datas.append(SheetData(df, fig, "Einsteiger 2"))

    df, fig = runs.plot_vehicles(by="name", names=ref.get_count_stations().names, ref_df=ref.get_stations())
    datas.append(SheetData(df, fig, "Link counts"))

    return datas
