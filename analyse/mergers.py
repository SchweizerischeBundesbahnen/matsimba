

def trips_with_persons(df, run):
    _df = run.get_persons().set_index("person_id")
    return df.merge(_df, how="left", left_on="person_id", right_index=True)


def legs_with_persons(df, run):
    _df = run.get_trips().set_index("journey_id")[["person_id"]]
    __df = df.merge(_df, how="left", left_on="journey_id", right_index=True)
    _df = run.get_persons().set_index("person_id")
    return __df.merge(_df, how="left", left_on="person_id", right_index=True)


def trips_with_acts(df, run):
    _df = run.get_acts().set_index("activity_id")
    __df = df.merge(_df, how="left", left_on="from_act", right_index=True, suffixes=("", "_from_act"))
    return __df.merge(_df, how="left", left_on="to_act", right_index=True, suffixes=("", "_to_act"))