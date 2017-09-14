from analyse.compare import _compare_by
from haltepunkte import make_simba_code


def pfahrt(runs, by, prozentual=False, func=None):
    df = _compare_by(runs, by, lambda r: r.get_legs(), func=func, values="trip_id", aggfunc="count")

    df = df.multiply([r.scale_factor for r in runs])

    if prozentual:
        df = df.div(df.sum())*100
    return df


def pkm(runs, by, prozentual=False, func=None):
    df = _compare_by(runs, by, lambda r: r.get_legs(), func=func, values="distance", aggfunc="sum")/1000.0

    df = df.multiply([r.scale_factor for r in runs])

    if prozentual:
        df = df.div(df.sum())*100
    return df


def _ea(runs, field, by=[], func=None):
    def _func(df, run):
        df = func(df, run)
        return df

    df = _compare_by(runs, [field+"_code"]+by, lambda r: r.get_legs(), func=_func, values=field, aggfunc="count")
    df = df.multiply([r.scale_factor for r in runs])
    return df


def einsteiger(runs, by=[], func=None):
    return _ea(runs, "boarding_stop", by, func)


def austeiger(runs, by=[], func=None):
    return _ea(runs, "alighting_stop", by, func)
