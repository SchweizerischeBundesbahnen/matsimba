import analyse.compare


def ea(runs, func):
    def _func(df, run):
        df = func(df, run)
        df.loc[:, "boarding"] = df.boarding * run.scale_factor
        df.loc[:, "alighting"] = df.alighting * run.scale_factor
        return df

    df = analyse.compare._compare_by(runs, "CODE",
                                     lambda r: r.get_stops(),
                                     func=_func,
                                     values=["boarding", "alighting"], aggfunc="sum")
    return df


