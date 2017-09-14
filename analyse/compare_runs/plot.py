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
    """
    :param runs:  list of Run objects
    :param by: column name or list of colum names
    :param func: can be used to merged data or filter dataframe
    :return: ax and dataframe
    """
    df = _compare_by(runs, by=by, get_data=lambda r: r.get_trips(), values="journey_id", aggfunc="count", func=func)

    if isinstance(by, list):
        _by = ", ".join(by)
    else:
        _by = by
    ax = df.plot(kind="bar", title="%s pro %s und Run" % ("#trips", _by))
    ax.set_ylabel("#trips")
    return ax, df


def number_legs_by(runs, by, func=None):
    df = _compare_by(runs, by=by, get_data=lambda r: r.get_legs(), values="trip_id", aggfunc="count", func=func)
    if isinstance(by, list):
        _by = ", ".join(by)
    else:
        _by = by
    ax = df.plot(kind="bar", title="%s pro %s und Run" % ("#legs", _by))
    ax.set_ylabel("#legs")
    return ax, df


def modalsplit_number_trips(runs, by, func=None):
    df = _compare_by(runs, by=by, get_data=lambda r: r.get_trips(), values="journey_id", aggfunc="count", func=func)
    df = df.div(df.sum())*100
    if isinstance(by, list):
        _by = ", ".join(by)
    else:
        _by = by
    ax = df.plot(kind="bar", title="Modalsplit bzgl. %s pro %s und Run" % ("#trips", _by))
    ax.set_ylabel("%")
    return ax, df


def _compare_by(runs, by, get_data, func=None, values="person_id", aggfunc="count"):
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
    return df

