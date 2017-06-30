import tempfile
import xlsxwriter
import pandas as pd


def insert_fig(worksheet, fig, row, col, kwargs):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as t:
        fig.savefig(t.file, bbox_inches='tight')
        worksheet.insert_image(row, col, t.name, **kwargs)
        return t.name


def make_report(path, acts):
    to_delete = []
    try:

        writer = pd.ExcelWriter(path, engine='xlsxwriter')

        workbook = writer.book

        grouped = acts.groupby("type").activity_id.count()
        pd.DataFrame(grouped).to_excel(writer, sheet_name='Activities')

        worksheet = [a for a in workbook.worksheets() if a.name == "Activities"][0]

        ax = grouped.plot("bar")
        fig = ax.get_figure()
        to_delete.append(insert_fig(worksheet, fig, 1, 5, {"options": {'x_scale': 0.5, 'y_scale': 0.5}}))
        plt.close(fig)

        acts["duration"] = (acts.end_time - acts.start_time) / 60. / 60.
        ax = acts.boxplot(column=["duration"], by=["type"], vert=False, figsize=(14, 10))
        fig = ax.get_figure()
        to_delete.append(insert_fig(worksheet, fig, 15, 5, {"options": {'x_scale': 0.5, 'y_scale': 0.5}}))
        plt.close(fig)

        for act in acts["type"].unique():
            print act

            worksheet = workbook.add_worksheet(act)
            ax = plot_time_hist(acts[acts["type"] == act])
            fig = ax.get_figure()
            to_delete.append(insert_fig(worksheet, fig, 1, 1, {"options": {'x_scale': 0.5, 'y_scale': 0.5}}))
            plt.close(fig)

            grouped = acts[acts["type"] == act].groupby("zone").count()
            fig, ax = analyse.map.choropleth(geojson, grouped, title_legend=act, coloumn="activity_id",
                                             vmin=1, vmax=grouped.max()["activity_id"], lims=rect)

            to_delete.append(insert_fig(worksheet, fig, 10, 1, {"options": {'x_scale': 0.5, 'y_scale': 0.5}}))
            plt.close(fig)

        workbook.close()

    except Exception as e:
        print e

    for f in to_delete:
        os.unlink(f)