import pandas as pd


def number_trips(runs):
    nb_trips = [len(run.get_trips())*run.scale_factor for run in runs]
    names = [run.name for run in runs]
    df = pd.DataFrame(nb_trips, index=names, columns=["#trips"])
    ax = df.plot(kind="bar",title="#trips pro Sensitivitaet", legend=False)
    ax.set_ylabel("#trips")
    return ax, df