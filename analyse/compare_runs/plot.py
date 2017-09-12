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


def number_trips_by(runs, by):
    df = analyse.compare.append([run.get_trips() for run in runs], [run.name for run in runs], column="Run")
    df = df.pivot_table(index=by, columns="Run", values="person_id", aggfunc="count", fill_value=0)
    ax = df.plot(kind="bar")
    return ax, df