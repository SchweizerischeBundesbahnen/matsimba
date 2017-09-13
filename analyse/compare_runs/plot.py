import pandas as pd
import analyse.compare


def number_trips(runs, by=None):
    if by is not None:
        return number_trips_by(runs, by)

    nb_trips = [len(run.get_trips())*run.scale_factor for run in runs]
    names = [run.name for run in runs]
    df = pd.DataFrame(nb_trips, index=names, columns=["#trips"])
    ax = df.plot(kind="bar",title="#trips pro Run", legend=False)
    ax.set_ylabel("#trips")
    return ax, df


def number_trips_by(runs, by, func=None):
    return compare_by(runs, by=by, get_data=lambda r: r.get_trips(), title="#trips", values="person_id",
               aggfunc="count", func=func)


def number_legs_by(runs, by, func=None):
    return compare_by(runs, by=by, get_data=lambda r: r.get_legs(), title="#legs", values="trip_id",
               aggfunc="count", func=func)


def compare_by(runs, by, get_data, func=None, title="#trips", values="person_id", aggfunc="count"):
    _dfs = []
    _names = []
    for run in runs:
        _names.append(run.name)
        _df = get_data(run)
        if func is not None:
            _df = func(_df, run)
        _dfs.append(_df)

    df = analyse.compare.append(_dfs, names=_names, column="Run")
    df = df.pivot_table(index=by, columns="Run", values=values, aggfunc=aggfunc, fill_value=0)
    ax = df.plot(kind="bar", title="%s pro %s und Run" % (title, by))
    ax.set_ylabel("#trips")
    return ax, df