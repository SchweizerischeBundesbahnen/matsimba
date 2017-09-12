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


def number_trips_by(runs, by, function=None):
    _dfs = []
    _names = []
    for run in runs:
        _names.append(run.name)
        _df = run.get_trips()
        if function is not None:
            _df = function(_df, run)
        _dfs.append(_df)

    df = analyse.compare.append(_dfs, names=_names, column="Run")
    df = df.pivot_table(index=by, columns="Run", values="person_id", aggfunc="count", fill_value=0)
    ax = df.plot(kind="bar", title="#trips pro %s und Run" % by)
    ax.set_ylabel("#trips")
    return ax, df