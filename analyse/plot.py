import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import glob


def set_matplotlib_params():
    plt.rcParams['figure.figsize'] = (16.0, 4.0)
    plt.rcParams.update({'font.size': 16})
    plt.style.use('ggplot')
    mpl.rcParams['axes.color_cycle'] = ["EB0000", "4C4C4C","2D327D", "348ABD", "7A68A6", "A60628", "467821", "CF4457", "188487", "E24A33", "FFFF00", "FF1DD8", "00FF8D"]
    mpl.rcParams['lines.linewidth'] = 2.5


def plot_score(folder):
    for file in glob.glob(os.path.join(folder, "*corestats.txt")):
        pd.read_csv(file, sep="\t", index_col=0).plot()


def plot_cumulative_mode(df, var="distance", max_value=10000):
    cats = np.linspace(0, max_value, 20)
    cats = np.insert(cats, 0, -1)
    cats = np.append(cats, 1000000000)
    df["cat"] = pd.cut(df[var], cats, include_lowest=True, right=True)

    fig, ax = plt.subplots(figsize=(16, 5))
    for mode in df["mode"].unique():
        _trips = df[df["mode"] == mode]
        grouped_trips = _trips.groupby(["cat"])
        a = grouped_trips.distance.count()
        a = a.cumsum()
        a = a.divide(len(_trips))
        a.plot(x="cat", ax=ax, label=mode)
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    ax.set_ybound([0, 1.1])


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
