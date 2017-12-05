import pandas as pd


def concat(dfs, names=None):
    _dfs = []
    if names is None:
        names = range(len(dfs))
    for _df, name in zip(dfs, names):
        df = _df.copy()
        df = pd.concat([df], keys=[name], names=['Run'], axis=1)
        #df.columns = pd.MultiIndex.from_product([df.columns, [name]])
        _dfs.append(df)
    df = pd.concat(_dfs, axis=1)
    #reorder
    df = df[names]
    #df.columns = df.columns.droplevel()
    return df[names]


def append(dfs, names, column="Run"):
    _dfs = []
    for df, name in zip(dfs, names):
        _df = df.copy()
        _df[column] = name
        _dfs.append(_df)

    return pd.concat(_dfs, ignore_index=True)


def _compare_by(runs, by, get_data, func=None, values="person_id", aggfunc="count"):
    _dfs = []
    _names = []
    for run in runs:
        _names.append(run.name)
        _df = get_data(run)
        if func is not None:
            _df = func(_df, run)
        _dfs.append(_df)

    df = append(_dfs, names=_names, column="Run")
    try:
        df = df.pivot_table(index=by, columns="Run", values=values, aggfunc=aggfunc, fill_value=0)
    except KeyError as e:
        raise Exception("Column %s is not in dataframe. Should you use a merger by passing a function to func?" % e)
    return df
