import analyse.compare
import analyse.plot
import pandas as pd


class RunsList(list):
    def get(self, name):
        for e in self:
            if e.name == name:
                return e

    @staticmethod
    def _plot(df, kind="bar", title="", cols=2.0, **kwargs):
        if "foreach" in kwargs:
            fig, axs = analyse.plot.plot_multi(df=df, cols=cols, kind=kind, **kwargs)
            fig.suptitle(title, fontsize=16)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            return df, fig

        else:
            ax = df.plot(kind=kind, title=title, figsize=(10, 5))
            analyse.plot.move_legend(ax)
            return df, ax.figure

    def _get(self, method, foreach=None, ref_df=None, **kwargs):
        names = [r.name for r in self]
        data = [method.im_func(r, foreach=foreach, **kwargs) for r in self]
        df = analyse.compare.concat(data, names)
        if foreach is None:
            df = df.swaplevel(0, 1, axis=1)
            df.columns = df.columns.droplevel()

        else:
            n = len(df.columns.levels)-1

            for i in range(n):
                df = df.stack()
            df = df.swaplevel(0, len(df.index.levels)-1, axis=0)

            #df.sort_index(inplace=True)

        columns = [r.name for r in self]

        if ref_df is not None:
            df = pd.concat([df, ref_df], axis=1)
            columns = ref_df.columns.tolist() + columns

        return df[columns]

    def get_nb_trips(self, **kwargs):
        return self._get(analyse.run.Run.calc_nb_trips, **kwargs)

    def plot_nb_trips(self, **kwargs):
        df = self.get_nb_trips(**kwargs)
        return self._plot(df=df, title="#trips pro %s und runs" % kwargs["by"], **kwargs)

    def get_pkm_trips(self, **kwargs):
        return self._get(analyse.run.Run.calc_dist_trips, **kwargs)

    def plot_pkm_trips(self, **kwargs):
        df = self.get_pkm_trips(**kwargs)
        return self._plot(df=df, title="pkm trips pro %s und runs" % kwargs["by"], **kwargs)

    def get_nb_legs(self, **kwargs):
        return self._get(analyse.run.Run.calc_nb_legs, **kwargs)

    def get_pkm_distr_legs(self, **kwargs):
        return self._get(analyse.run.Run.calc_dist_distr_legs, **kwargs)

    def get_pkm_distr_trips(self, **kwargs):
        return self._get(analyse.run.Run.calc_dist_distr_trips, **kwargs)

    def plot_pkm_distr_legs(self, **kwargs):
        df = self.get_pkm_distr_legs(**kwargs)
        return self._plot(df=df, kind="line", title="", **kwargs)

    def plot_pkm_distr_trips(self, **kwargs):
        df = self.get_pkm_distr_trips(**kwargs)
        return self._plot(df=df, kind="line", title="", **kwargs)

    def plot_nb_legs(self, **kwargs):
        df = self.get_nb_legs(**kwargs)
        return self._plot(df=df, title="#legs pro %s und runs" % kwargs["by"], **kwargs)

    def get_pkm_legs(self, **kwargs):
        return self._get(analyse.run.Run.calc_dist_legs, **kwargs)

    def plot_pkm_legs(self, **kwargs):
        df = self.get_pkm_legs(**kwargs)
        return self._plot(df=df, title="pkm legs pro %s und runs" % kwargs["by"], **kwargs)

    def get_einsteiger(self, **kwargs):
        return self._get(analyse.run.Run.calc_einsteiger, **kwargs)

    def plot_einsteiger(self, **kwargs):
        df = self.get_einsteiger(**kwargs)
        if df.index.size>100:
            raise ValueError("Index size to large to be plotted")
        return self._plot(df=df, title="Einsteiger pro CODE", **kwargs)

    def get_vehicles(self, **kwargs):
        return self._get(analyse.run.Run.calc_vehicles, **kwargs)

    def plot_vehicles(self,  **kwargs):
        df = self.get_vehicles(**kwargs)
        if df.index.size>100:
            raise ValueError("Index size to large to be plotted")
        return self._plot(df=df, title="Fahrzeuge", **kwargs)



