import pandas as pd


def concat(dfs, names=None):
    _dfs = []
    if names is None:
        names = range(len(dfs))

    for _df, name in zip(dfs, names):
        df = _df.copy()
        df.columns = pd.MultiIndex.from_product([df.columns, [name]])
        _dfs.append(df)
    return pd.concat(_dfs, axis=1)