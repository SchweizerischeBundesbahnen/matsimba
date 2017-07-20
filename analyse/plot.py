import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import glob
import datetime
import analyse.compare


def set_matplotlib_params():
    plt.rcParams['figure.figsize'] = (16.0, 4.0)
    plt.rcParams.update({'font.size': 16})
    plt.style.use('ggplot')
    mpl.rcParams['axes.color_cycle'] = ["EB0000", "4C4C4C","2D327D", "348ABD", "7A68A6", "A60628", "467821", "CF4457", "188487", "E24A33", "FFFF00", "FF1DD8", "00FF8D"]
    mpl.rcParams['lines.linewidth'] = 2.5


def get_score(folder):
    for file in glob.glob(os.path.join(folder, "*corestats.txt")):
        return pd.read_csv(file, sep="\t", index_col=0)


def plot_score(folder, names=None):
    """
    Plot score of MATSim run. Folder must be path of the output folder
    :param folder: either list or single path to output folder
    :param names: if folder is a list, should be the corresponding names
    :return: ax
    """
    if isinstance(folder, list):
        datas = []
        for f in folder:
            datas.append(get_score(f))
        ax = analyse.compare.concat(datas, names).plot()
    else:
        ax = get_score(folder).plot()
    return move_legend(ax)


def plot_cumulative_mode(df, var="distance", max_value=10000, ax=None):
    cats = np.linspace(0, max_value, 20)
    cats = np.insert(cats, 0, -1)
    cats = np.append(cats, 1000000000)
    df["cat"] = pd.cut(df[var], cats, include_lowest=True, right=True)

    if ax is None:
        fig, ax = plt.subplots(figsize=(16, 5))
    for mode in df["mode"].unique():
        _trips = df[df["mode"] == mode]
        grouped_trips = _trips.groupby(["cat"])
        a = grouped_trips.distance.count()
        a = a.cumsum()
        a = a.divide(len(_trips))
        a.plot(x="cat", ax=ax, label=mode)
    ax = move_legend(ax)
    ax.set_ybound([0, 1.1])
    return ax


def move_legend(ax):
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    return ax


def get_timing(folder):
    filename = glob.glob(os.path.join(folder, "*stopwatch.txt"))[0]
    stopwatch = pd.DataFrame.from_csv(filename, sep="\t")

    columns = ["replanning", "beforeMobsimListeners", "mobsim", "afterMobsimListeners", "scoring", "dump all plans",
               "compare with counts", "iterationEndsListeners", "iteration"]
    for c in columns:
        try:
            stopwatch.loc[stopwatch[c].isnull(), c] = "00:00:00"

            stopwatch[c] = stopwatch[c].map(
                lambda x: int(x.split(":")[0]) * 3600 + int(x.split(":")[1]) * 60 + int(x.split(":")[2]))
        except:
            pass
    return stopwatch


def plot_timing(folder):
    stopwatch = get_timing(folder)
    columns = ["replanning", "beforeMobsimListeners", "mobsim", "afterMobsimListeners", "scoring", "dump all plans",
               "compare with counts", "iterationEndsListeners"]
    ax = stopwatch[[c for c in columns if c in stopwatch.columns]].plot(kind="bar", stacked=True)
    return move_legend(ax)


def plot_leg_histogram(folder, var="departures_all", iters=None):
    folder = os.path.join(folder, "ITERS")
    if iters is None:
        iters = []
        for it in glob.glob(os.path.join(folder, "*")):
            iters.append(int(it.split(".")[-1]))

    iters.sort()

    fig, ax = plt.subplots(figsize=(16, 5))

    for it in iters:
        _path = glob.glob(os.path.join(folder, "it.%i" % it, "*legHist*"))
        if len(_path) > 0:
            df = pd.DataFrame.from_csv(_path[0], sep="\t")
            df[var].plot(ax=ax, label=it)
    ax.legend()
    ax.set_title(var)


def plot_modalsplit(trips):
    fig = plt.figure(figsize=(15, 4.5))
    ax = fig.add_subplot(1, 3, 1)
    trips.groupby("mode").distance.count().rename(columns={"distance": "count"}).plot(kind="pie", ax=ax)
    ax = fig.add_subplot(1, 3, 2)
    trips.groupby("mode").distance.sum().plot(kind="pie", ax=ax)
    ax = fig.add_subplot(1, 3, 3)
    trips["duration"] = trips.end_time-trips.start_time
    trips.groupby("mode").duration.sum().plot(kind="pie", ax=ax)
    return fig


def make_all_plots(trips, journeys, activities, output_folder):
    set_matplotlib_params()

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 7))
    trips.groupby("mode").distance.sum().plot(kind="pie", ax=ax)
    fig.savefig(os.path.join(output_folder, "modalsplit_trips_distance_sum.png"))

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 7))
    journeys.groupby("main_mode").distance.count().plot(kind="pie", ax=ax)
    fig.savefig(os.path.join(output_folder, "modalsplit_journeys_distance_count.png"))

    fig, ax = plt.subplots(1, 1, figsize=(6.5, 7))
    journeys.groupby("main_mode").distance.sum().plot(kind="pie", ax=ax)
    fig.savefig(os.path.join(output_folder, "modalsplit_journeys_distance_sum.png"))

    journeys["start_minute"] = journeys.start_time.map(lambda x: x // 60)
    fig, ax = plt.subplots(figsize=(16, 5))
    for mode in journeys["main_mode"].unique():
        _journeys = journeys[journeys["main_mode"] == mode]
        _journeys.groupby("start_minute").distance.count().plot(ax=ax, label=mode)
    fig.savefig(os.path.join(output_folder, "departure_time_modes.png"))

    bins = [-1, -0.0001, 500, 1500, 2500, 3500, 4500, 5500, 15000, np.inf]
    group_names = ["0 km", "0.25 km", "1 Km", "2 km", "3 km", "4 km", "5 km", "10 km", ">10 km"]

    journeys["distance_categorie"] = pd.cut(journeys.distance, bins, labels=group_names)
    trips["distance_categorie"] = pd.cut(trips.distance, bins, labels=group_names)

    fig, ax = plt.subplots(figsize=(16, 5))
    for mode in trips["mode"].unique():
        _trips = trips[trips["mode"] == mode]
        grouped_trips = _trips.groupby(["distance_categorie"])
        a = grouped_trips.duration.count()
        a = a.cumsum()
        a = a.divide(len(_trips))
        a.plot(ax=ax, label=mode)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_ybound([0, 1.1])
    fig.savefig(os.path.join(output_folder, "trips_distance_cdf.png"))

    trips["duration"] = trips.end_time-trips.start_time
    journeys["duration"] = journeys.end_time-journeys.start_time
    bins = [-1, 0, 2.5 * 60, 7.5 * 60, 12.5 * 60, 17.5 * 60, 22.5 * 60, 27.5 * 60, 32.5 * 60, np.inf]
    group_names = ["0  Min", "2.5 Min", "5 Min", "10 Min", "15 Min", "20 Min", "25 Min", "30 Min", ">30 Min"]
    journeys["duration_categories"] = pd.cut(journeys.duration, bins, labels=group_names)
    trips["duration_categories"] = pd.cut(trips.duration, bins, labels=group_names)

    fig, ax = plt.subplots(figsize=(16, 5))
    for mode in trips["mode"].unique():
        _trips = trips[trips["mode"] == mode]
        grouped_trips = _trips.groupby(["duration_categories"])
        a = grouped_trips.duration.count()
        a = a.cumsum()
        a = a.divide(len(_trips))
        a.plot(ax=ax, label=mode)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_ybound([0, 1.1])
    fig.savefig(os.path.join(output_folder, "trips_duration_cdf.png"))

    fig, ax = plt.subplots(figsize=(16, 12))
    merged_journeys = pd.merge(journeys, activities, how="left", left_on="from_act", right_on="activity_id",
                               suffixes=('', '_fromact'))
    merged_journeys = pd.merge(merged_journeys, activities, how="left", left_on="to_act", right_on="activity_id",
                               suffixes=('', '_toact'))
    merged_journeys.groupby([merged_journeys.type_toact, merged_journeys.main_mode]).distance.sum().divide(
        journeys.distance.sum()).unstack().plot(kind="barh", by="main_mode", ax=ax, stacked=True)
    fig.savefig(os.path.join(output_folder, "modal_split_to_act_distance.png"))


def plot_time_hist(_df):
    start_time = _df.start_time.apply(lambda x: datetime.datetime.fromtimestamp(x))
    end_time = _df.end_time.apply(lambda x: datetime.datetime.fromtimestamp(x))

    open = pd.concat([pd.Series(1, start_time), pd.Series(-1, end_time)]).resample("10Min", how="sum").cumsum()
    ax = open.plot(kind="bar")
    xticks = ax.get_xticks()
    xticklabels = ax.get_xticklabels()

    ax.set_xticks(xticks[::4])

    ax.set_xticklabels([tl.get_text().split(" ")[1][:-3] for tl in xticklabels][::4])
    return ax


def plot_boxplot_duration(df):
    df["duration"] = (df.end_time - df.start_time) / 60. / 60.
    ax = df.boxplot(column=["duration"], by=["type"], vert=False, figsize=(14, 10))
    return ax


def _get_departures_sum(folder):
    folder = os.path.join(folder, "ITERS")
    iters = []
    for it in glob.glob(os.path.join(folder, "*")):
        iters.append(int(it.split(".")[-1]))

    iters.sort()

    dfs = []
    names = []
    for it in iters:
        _path = glob.glob(os.path.join(folder, "it.%i" % it, "*legHist*"))
        if len(_path) > 0:
            df = pd.DataFrame.from_csv(_path[0], sep="\t")
            dfs.append(df)
            names.append(it)
    df = analyse.compare.concat(dfs, names)
    return pd.DataFrame(df.sum()).swaplevel(0, 1).unstack()[0]


def plot_departures_sum(folder, var_list=("departures_bike", "departures_car", "departures_pt",
                                          "departures_ride", "departures_walk"), names=None):
    """
    :param folder: path or list of paths of output folders
    :param names: names for dataframes if folder is a list
    :param var_list: Columns to be plotted
    :return: ax
    """

    if not isinstance(folder, list):
        df = _get_departures_sum(folder)
        cols = [col for col in df.columns if col in var_list]
        ax = df[cols].plot(legend=True)
    else:
        dfs = []
        for f in folder:
            dfs.append(_get_departures_sum(f))
        _dfs = analyse.compare.concat(dfs=dfs, names=names)
        ax = _dfs[list(var_list)].plot(legend=True)

    return move_legend(ax)


def plot_plans(planelements, end_time=35 * 60 * 60):
    plan_ids = planelements.plan_id.unique()

    n = len(plan_ids)
    f = plt.figure(figsize=(20, n * 1.0))
    ax = f.add_subplot(1, 1, 1)
    text = []
    for i, plan_id in enumerate(plan_ids):
        times = []
        pes = []
        for index, b in planelements[planelements.plan_id==plan_id].iterrows():
            if b["type"] == "activity":
                pes.append(b["activity_type"])
                times.append(b["start_time"])
                times.append(b["end_time"])
            else:
                pes.append(b["mode"])
        for j, t in enumerate(times[1:-1:2]):
            ii = times.index(t)
            t0 = float(times[ii - 1])
            t1 = float(times[ii])
            ax.plot([t0, t0], [0.4 + i, 0.7 + i], c="k")
            ax.plot([t1, t1], [0.4 + i, 0.7 + i], c="k")
            ax.plot([t0, t1], [0.5 + i, 0.5 + i], c="k")

        t0 = float(times[-2])
        t1 = end_time
        ax.plot([t0, t0], [0.4 + i, 0.7 + i], c="k")
        ax.plot([t1, t1], [0.4 + i, 0.7 + i], c="k")
        ax.plot([t0, t1], [0.5 + i, 0.5 + i], c="k")
        text.append([p for p in pes] + [b["plan_score"], b["selected"]])

    ax.axis('off')
    f.tight_layout()
    return ax, pd.DataFrame(text)
