import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib as mpl
from matplotlib import cm
import shapely.geometry as sg
import numpy as np


class MplColorHelper:
    def __init__(self, cmap_name, start_val, stop_val):
        self.start_val = start_val
        self.stop_val = stop_val
        self.cmap_name = cmap_name
        self.cmap = plt.get_cmap(cmap_name)
        self.norm = mpl.colors.Normalize(vmin=start_val, vmax=stop_val)
        self.scalarMap = cm.ScalarMappable(norm=self.norm, cmap=self.cmap)

    def get_rgb(self, val):
        return self.scalarMap.to_rgba(val)

    def plot_bar(self, name, fontsize=10, alpha=1.0, ax=None):
        if ax is None:
            fig, ax = plt.subplots(figsize=(5, 0.2))

        gradient = np.linspace(self.start_val, self.stop_val, 256)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, aspect='auto', cmap=self.cmap_name, alpha=alpha)
        xmin = ax.get_xlim()[0]
        xmax = ax.get_xlim()[1]
        x_text = (xmin + xmax) / 2.
        y_text = ax.get_ylim()[0]
        ax.text(x_text, y_text, name, va='top', ha='center', fontsize=fontsize)

        ax.text(xmin, y_text, self.start_val, va='top', ha='center', fontsize=fontsize)
        ax.text(xmax, y_text, self.stop_val, va='top', ha='left', fontsize=fontsize)
        ax.set_axis_off()
        return ax


def map_journeys(geojson, data, property="GMDNAME", color="#F6F6F6", lims=None):
    fig = plt.figure()
    axs = fig.add_subplot(111)
    coordinates = {}

    for feature in geojson["features"]:
        geo = feature["geometry"]
        shape = sg.shape(geo)

        coordinates[feature["properties"][property]] = [shape.centroid.x, shape.centroid.y]

        if shape.type == "MultiPolygon":
            for geo in shape.geoms:
                xs, ys = geo.exterior.xy
                axs.fill(xs, ys, fc=color, ec='k')

        else:
            xs, ys = shape.exterior.xy
            axs.fill(xs, ys, fc=color, ec='k')

    if lims is not None:
        axs.set_xlim(lims[0])
        axs.set_ylim(lims[1])

    w = axs.get_xbound()[1]-axs.get_xbound()[0]
    h = axs.get_ybound()[1]-axs.get_ybound()[0]

    fig.set_size_inches(width, h/w*width )

    axs.axis('off')

    for od in data.index:
        o = od[0]
        d = od[1]
        from_coord = coordinates[o]
        to_coord = coordinates[d]

        axs.arrow(from_coord[0], from_coord[1],
                  to_coord[0] - from_coord[0], to_coord[1] - from_coord[1],
                  head_width=3000,
                  head_length=3000, fc='k', ec='k', lw=2, alpha=1.0)

    return fig, axs


def choropleth(geojson, data, title_legend="Value", property="GMDNAME", coloumn="activity_id", alpha=1.0, cmap="jet", vmin=1, vmax=30000, width=15, lims=None):
    mmm = MplColorHelper(cmap, vmin, vmax)

    fig = plt.figure()
    axs = fig.add_subplot(111)

    for feature in geojson["features"]:
        gmd = feature["properties"][property]
        value = 0
        try:
            value = data.loc[gmd][coloumn]
        except:
            pass

        geo = feature["geometry"]
        c = mmm.get_rgb(value)
        if value == 0:
            c = "#F6F6F6"
        new_shape = sg.shape(geo)
        if new_shape.type == "MultiPolygon":
            for geo in new_shape.geoms:
                xs, ys = geo.exterior.xy
                axs.fill(xs, ys, alpha=alpha, fc=c, ec='k')

        else:
            xs, ys = new_shape.exterior.xy
            axs.fill(xs, ys, alpha=alpha, fc=c, ec='k')

    if lims is not None:
        axs.set_xlim(lims[0])
        axs.set_ylim(lims[1])

    w = axs.get_xbound()[1]-axs.get_xbound()[0]
    h = axs.get_ybound()[1]-axs.get_ybound()[0]

    fig.set_size_inches(width, h/w*width )
    axs.axis('off')
    # fig.set_facecolor('#F6F6F6')
    ax_ = fig.add_axes([0.1, 0.9, 0.2, 0.02])
    mmm.plot_bar(title_legend, alpha=alpha, ax=ax_)
    return fig, axs
