import pandas as pd
import io
from variable import *
import logging
import analyse.run
import analyse.runs
import analyse.compare


class SheetData:
    def __init__(self, df, fig, name):
        logging.info("Making %s" % name)
        if not isinstance(df, list):
            df = [df]
        self.dfs = df
        self.fig = fig
        self.name = name


def make_report(runs, filename, ref=None):
    datas = get_datas(runs=runs, ref=ref)
    _make_report(datas=datas, filename=filename)


def _make_report(datas, filename):
    logging.info("Writing report")
    buffers = []

    def get_buffer(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        fig.clf()
        buf.seek(0)
        buffers.append(buf)
        return buf

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')

    worksheet = writer.book.add_worksheet("TableOfContents")
    _sheets = {}
    for i, data in enumerate(datas):
        sheet = data.name[:20]
        if sheet in _sheets:
            _sheets[sheet] += 1
            sheet = sheet + str(_sheets[sheet])
        else:
            _sheets[sheet] = 1
        data.sheet = sheet
        link = data.sheet
        if data.fig is None:
            link += "_data"
        worksheet.write_url(i + 1, 1, url="internal:'%s'!A1" % link, string=data.name)

    for data in datas:
        dfs = data.dfs
        if data.fig is not None:
            buf = get_buffer(data.fig)
            sheet = writer.book.add_worksheet(data.sheet)
            sheet.insert_image('A1', "aa", {'image_data': buf})
        startcol = 1
        for df in dfs:
            df.to_excel(writer, sheet_name=data.sheet + "_data", startrow=1, startcol=startcol, merge_cells=False,
                        encoding="utf-8")
            startcol += 3 + len(df.columns) + df.index.nlevels

    writer.save()

    for buf in buffers:
        buf.close()

    logging.info("Done writing file")


def get_datas(runs, ref):
    datas = []

    mzmv = ref.get_mzmv_run()

    try:
        title = "Modal Split PF"

        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title}
        df, ax = runs.plot_nb_trips(**kwargs)
        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)

        datas.append(SheetData([df, _df], ax, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title, "foreach": SUBPOPULATION}
        df, ax = runs.plot_nb_trips(**kwargs)
        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)
        datas.append(SheetData([df, _df], ax, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation und PW-Verfuergbarkeit"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title,
                  "foreach": [SUBPOPULATION, CARAVAIL]}
        df, fig = runs.plot_nb_trips(**kwargs)
        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)
        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation und OV-Abonnement"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title,
                  "foreach": [SUBPOPULATION, SEASON_TICKET]}
        df, fig = runs.plot_nb_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation und Raumtyp"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title,
                  "foreach": [SUBPOPULATION, RAUMTYP]}
        df, fig = runs.plot_nb_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation und professionelle Gruppe"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title,
                  "foreach": [SUBPOPULATION, "work: employment status"]}
        df, fig = runs.plot_nb_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PF pro Subpopulation, PK-Verfuergbarkeit und OV-Abonnement"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title,
                  "foreach": [SUBPOPULATION, CARAVAIL, SEASON_TICKET]}
        df, fig = runs.plot_nb_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_nb_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    # PKM
    try:
        title = "Modal Split PKM"
        kwargs = {"by": MAIN_MODE, "ref_run": mzmv, "percent": True, "title": title}
        df, ax = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], ax, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation"
        kwargs = {"by": MAIN_MODE, "foreach": SUBPOPULATION, "ref_run": mzmv, "percent": True, "title": title}
        df, ax = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], ax, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation und PW-Verfuergbarkeit"
        kwargs = {"by": MAIN_MODE, "foreach": [SUBPOPULATION, CARAVAIL], "ref_run": mzmv, "percent": True,
                  "title": title}
        df, fig = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation und OV-Abonnement"
        kwargs = {"by": MAIN_MODE, "foreach": [SUBPOPULATION, SEASON_TICKET], "ref_run": mzmv, "percent": True,
                  "title": title}
        df, fig = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation und Raumtyp"
        kwargs = {"by": MAIN_MODE, "foreach": [SUBPOPULATION, RAUMTYP], "ref_run": mzmv, "percent": True,
                  "title": title}
        df, fig = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation und professionelle Gruppe"
        kwargs = {"by": MAIN_MODE, "foreach": [SUBPOPULATION, "work: employment status"], "ref_run": mzmv,
                  "percent": True, "title": title}
        df, fig = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split PKM pro Subpopulation, PW-Verfuergbarkeit und OV-Abonnement"
        kwargs = {"by": MAIN_MODE, "foreach": [SUBPOPULATION, CARAVAIL, SEASON_TICKET], "ref_run": mzmv,
                  "percent": True, "title": title}
        df, fig = runs.plot_pkm_trips(**kwargs)

        kwargs["percent"] = False
        _df = runs.get_pkm_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    ### Distanzklasse

    try:
        title = "Modal Split pro Distanzklasse"
        kwargs = {"foreach": [MAIN_MODE], "percent": True, "rotate": True, "ref_run": mzmv, "title": title,
                  "inverse_percent_axis": True}
        df, fig = runs.plot_pkm_distr_trips(**kwargs)

        kwargs["percent"] = False
        _df, _ = runs.plot_pkm_distr_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split pro Distanzklasse und Subpopulation"
        kwargs = {"foreach": [SUBPOPULATION, MAIN_MODE], "percent": True, "rotate": True, "ref_run": mzmv,
                  "title": title, "inverse_percent_axis": True, "percent_level": [SUBPOPULATION]}
        df, fig = runs.plot_pkm_distr_trips(**kwargs)

        kwargs["percent"] = False
        _df, _ = runs.plot_pkm_distr_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Modal Split pro Distanzklasse, Subpopulation, PW-Verfuergbarkeit und OV-Abonnement"

        kwargs = {"foreach": [SUBPOPULATION, CARAVAIL, SEASON_TICKET, MAIN_MODE], "percent": True, "rotate": True,
                  "ref_run": mzmv, "title": title, "inverse_percent_axis": True, "percent_level": [SUBPOPULATION]}
        df, fig = runs.plot_pkm_distr_trips(**kwargs)

        kwargs["percent"] = False
        _df, _ = runs.plot_pkm_distr_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))

    except Exception as e:
        logging.exception(e)

    try:
        title = "Reisezeit pro Subpopulation und Verkehrsmittel"

        kwargs = {"foreach": [SUBPOPULATION, MAIN_MODE], "percent": True, "rotate": True, "title": title}
        df, fig = runs.plot_duration_trips(**kwargs)

        kwargs["percent"] = False
        _df, _ = runs.plot_duration_trips(**kwargs)

        datas.append(SheetData([df, _df], fig, title))

    except Exception as e:
        logging.exception(e)

    try:
        title = "Aggregierte Strome"
        df = runs.get_nb_trips(by=[SUBPOPULATION, "from_N_Gem", "to_N_Gem", MAIN_MODE])
        datas.append(SheetData(df, None, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahnhof Einsteiger - Auswahl"
        df, fig = runs.plot_einsteiger(by="03_Stop_Code_boarding", codes=ref.stations, ref_run=ref.get_pt_run(),
                                       title=title, ref_df=ref.get_bahnhof_boarding().loc[ref.stations])
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahnhof Einsteiger - Auswahl (SBF)"
        df, fig = runs.plot_einsteiger(by="03_Stop_Code_boarding", codes=ref.stations, ref_run=ref.get_pt_run(),
                                       title=title,
                                       simba_only=True)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahnhof Einsteiger - Alle"
        df, fig = runs.plot_boarding_scatter(by="03_Stop_Code_boarding", pt_run=ref.get_pt_run(), title=title,
                                             ref_df=ref.get_bahnhof_boarding())
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahnhof Einsteiger - Alle (SBF)"
        df, fig = runs.plot_boarding_scatter(by="03_Stop_Code_boarding", pt_run=ref.get_pt_run(), title=title,
                                             simba_only=True)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahnhof Einsteiger - Alle - Subpopulation"
        df = runs._get(analyse.run.Run.calc_einsteiger, by="03_Stop_Code_boarding", foreach="subpopulation")
        datas.append(SheetData(df, None, title))
    except Exception as e:
        logging.exception(e)

    # try:
    #    df, fig = runs.plot_vehicles(by="name", names=ref.get_count_stations().name.unique().tolist(),
    #                                 ref_df=ref.get_count_stations_volume())
    #    datas.append(SheetData(df, fig, "Link counts"))
    # except Exception as e:
    #    logging.exception(e)
    try:
        df, fig = runs.plot_vehicles(ref_run=ref.get_astra_run(), title="ASTRA Messstellen")
        datas.append(SheetData(df, fig, "ASTRA Messstellen"))
    except Exception as e:
        logging.exception(e)

    try:
        df, fig = runs.plot_pt_pkm(by="06_OperatorName", ref_run=ref.get_pt_run())
        datas.append(SheetData(df, fig, "OV PKM pro Betreiber"))
    except Exception as e:
        logging.exception(e)

    try:
        title = r"OEV PKM pro VSys"
        df, fig = runs.plot_pt_pkm(by="08_TSysName", indices=ref.tsys_names, ref_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = r"OEV Teilwege pro VSys und Distanzklasse"
        df, fig = runs.plot_pt_pkm_distr_legs(ref_run=ref.get_pt_run(), foreach=["08_TSysName"], rotate=True,
                                              percent=False, title=title, share_y=False)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = r"OEV Teilwege Tagesganglinie"
        df, fig = runs.plot_nb_legs(by=CAT_START_TIME, foreach="mode", kind="line", ref_run=ref.get_pt_run(),
                                    title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = r"Bahn Wege - Distanz Verteilung (SBF)"
        df, fig = runs.plot_pt_dist_distr_trips(simba_only=True, ref_run=ref.get_pt_run(), rotate=True, title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = r"Bahn Wege - Distanz Verteilung - Pro Abo (SBF)"
        df, fig = runs.plot_pt_dist_distr_trips(simba_only=True, foreach=[SUBPOPULATION, SEASON_TICKET], rotate=True,
                                                title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn Wege - UH Verteilung (SBF)"
        df, fig = runs.plot_pt_uh(simba_only=True, ref_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn Wege - PF - Bhf-Bhf (SBF)"
        df, fig = runs.plot_pt_skims(name="PF", pt_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn Wege - UH - Bhf-Bhf (SBF)"
        df, fig = runs.plot_pt_skims(name="uh", pt_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn Wege - BZ - Bhf-Bhf (SBF)"
        df, fig = runs.plot_pt_skims(name="bz", pt_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn Wege - Distanz - Bhf-Bhf (SBF)"
        df, fig = runs.plot_pt_skims(name="distance", pt_run=ref.get_pt_run(), title=title)
        datas.append(SheetData(df, fig, title))
    except Exception as e:
        logging.exception(e)

    try:
        title = "Bahn globale Statistiken"
        df = runs.get_pt_table(pt_run=ref.get_pt_run())
        datas.append(SheetData(df, None, title))
    except Exception as e:
        logging.exception(e)

    return datas
