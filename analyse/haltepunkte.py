import analyse.compare


def make_simba_code(stops):
    stops["is_simba"] = stops.line.str.match(r'\d{3}-[A-Z]-.*')
    stops["CODE"] = None
    stops.loc[stops.is_simba, "CODE"] = stops[stops.is_simba].stop_id.apply(lambda x: x.split("_")[1])
    return stops


def ea(runs):
    def func(df, run):
        df = make_simba_code(df)[["CODE", "boarding", "alighting"]].copy()
        df.loc[:, "boarding"] = df.boarding * run.scale_factor
        df.loc[:, "alighting"] = df.alighting * run.scale_factor
        return df

    df = analyse.compare._compare_by(runs, "CODE",
                                     lambda r: r.get_stops(),
                                     func=func,
                                     values=["boarding", "alighting"], aggfunc="sum")
    return df


