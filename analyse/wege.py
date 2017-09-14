from analyse.compare_runs.plot import _compare_by


def pfahrt(runs, by, prozentual=False, func=None):
    df = _compare_by(runs, by, lambda r: r.get_trips(), func=func, values="person_id", aggfunc="count")
    if prozentual:
        df = df.div(df.sum())*100
    return df

