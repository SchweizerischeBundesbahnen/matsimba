from analyse.compare import _compare_by


def pfahrt(runs, by, prozentual=False, func=None):
    df = _compare_by(runs, by, lambda r: r.get_trips(), func=func, values="journey_id", aggfunc="count")
    if prozentual:
        df = df.div(df.sum())*100
    return df


def pkm(runs, by, prozentual=False, func=None):
    df = _compare_by(runs, by, lambda r: r.get_trips(), func=func, values="distance", aggfunc="sum")/1000.0
    if prozentual:
        df = df.div(df.sum())*100
    return df

