from analyse.compare import _compare_by


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

