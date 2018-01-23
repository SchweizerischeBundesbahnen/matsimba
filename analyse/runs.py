import analyse.compare
import analyse.plot
import pandas as pd
import analyse.run


class RunsList(list):
    def get(self, name):
        for e in self:
            if e.name == name:
                return e

    @staticmethod
    def _plot(df, kind="bar", title="", cols=2.0, xs_index=None, **kwargs):
        """
        :param df:
        :param kind:
        :param title:
        :param cols:
        :param xs_index: is used to sort the x axis for plotting
        :param kwargs:
        :return:
        """
        if "foreach" in kwargs:
            fig, axs = analyse.plot.plot_multi(df=df, cols=cols, kind=kind, xs_index=xs_index, **kwargs)
            fig.suptitle(title, fontsize=16)
            fig.tight_layout(rect=[0, 0.03, 1, 0.95])
            return df, fig

        else:
            if xs_index is None:
                xs_index = df.index

            ax = df.loc[xs_index].plot(kind=kind, title=title, figsize=(10, 5))
            analyse.plot.move_legend(ax)
            fig = ax.figure
            fig.tight_layout()
            return df, fig

    def _get(self, method, foreach=None, ref_df=None, ref_run=None, **kwargs):
        names = [r.name for r in self]
        data = [method.im_func(r, foreach=foreach, **kwargs) for r in self]
        df = analyse.compare.concat(data, names)
        if foreach is None:
            df = df.swaplevel(0, 1, axis=1)
            df.columns = df.columns.droplevel()

        else:
            n = len(df.columns.levels) - 1

            for i in range(n):
                df = df.stack()
            df = df.swaplevel(0, len(df.index.levels) - 1, axis=0)
            # df.sort_index(inplace=True)

        columns = [r.name for r in self]

        if ref_df is not None:
            df = pd.concat([df, ref_df], axis=1)
            columns = ref_df.columns.tolist() + columns

        if ref_run is not None:
            _runs = RunsList()
            _runs.append(ref_run)
            _df = _runs._get(method=method, foreach=foreach, **kwargs)
            df = pd.concat([_df, df], axis=1)
            columns = _df.columns.tolist() + columns

        return df[columns].sort_index()

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
        return self._plot(df=df, kind="line", title="", xs_index=analyse.run.distance_labels, **kwargs)

    def plot_pkm_distr_trips(self, **kwargs):
        df = self.get_pkm_distr_trips(**kwargs)
        return self._plot(df=df, kind="line", title="", xs_index=analyse.run.distance_labels, **kwargs)

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
        return self._plot(df=df, title="Einsteiger pro CODE", **kwargs)

    def get_vehicles(self, **kwargs):
        return self._get(analyse.run.Run.calc_vehicles, **kwargs)

    def plot_vehicles(self, **kwargs):
        df = self.get_vehicles(**kwargs)
        return self._plot(df=df, title="Fahrzeuge", **kwargs)

    def get_pt_pkm(self, **kwargs):
        return self._get(analyse.run.Run.calc_pt_pkm, **kwargs)

    def plot_pt_pkm(self, **kwargs):
        df = self.get_pt_pkm(**kwargs)
        return self._plot(df=df, title="", **kwargs)

    def plot_pt_dist_distr_trips(self, **kwargs):
        df = self._get(analyse.run.Run.calc_pt_dist_distr_trips, **kwargs)
        return self._plot(df=df, title="sfsfd", kind="line", xs_index=analyse.run.distance_labels, **kwargs)

    def plot_pt_pkm_distr_legs(self, **kwargs):
        df = self._get(analyse.run.Run.calc_dist_distr_pt_legs, **kwargs)
        return self._plot(df=df, kind="line", title="dads", **kwargs)

    def plot_pt_nb_trips(self, **kwargs):
        df = self._get(analyse.run.Run.calc_pt_nb_trips, **kwargs)
        return self._plot(df=df, title="", **kwargs)

    def plot_pt_uh(self, **kwargs):
        df = self._get(analyse.run.Run.calc_pt_uh, **kwargs)
        return self._plot(df=df, title="", **kwargs)

    def plot_pt_skims(self, pt_run, **kwargs):
        df = self._get(analyse.run.Run.get_skim_simba, ref_run=pt_run, **kwargs)
        fig = analyse.plot.plot_scatter(df=df, ref_name=pt_run.name, title="", **kwargs)
        return df, fig

    def prepare(self, **kwargs):
        for run in self:
            run.prepare(**kwargs)
