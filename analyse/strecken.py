from compare import _compare_by


def fahrzeuge(runs, link_ids, func=None):
    def f(r):
        df = r.get_linkvolumes()
        return df.set_index("link_id").loc[link_ids].reset_index()

    df = _compare_by(runs, "link_id", get_data=f, func=func, values="volume", aggfunc="sum")

    df = df.multiply([r.scale_factor for r in runs])

    return df