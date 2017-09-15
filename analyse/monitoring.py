import analyse.plot


def plot_timing(run):
    return analyse.plot.plot_timing(run.path)


def plot_leg_histogram(run, var, iters):
    return analyse.plot.plot_leg_histogram(run.path, var, iters)


def plot_departures(runs):
    return analyse.plot.plot_departures_sum([r.path for r in runs], names=[r.name for r in runs])


def plot_score(runs):
    return analyse.plot.plot_score([r.path for r in runs], names=[r.name for r in runs])
