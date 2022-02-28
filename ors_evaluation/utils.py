#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Utility functions"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import random
from shapely.geometry import Point
import matplotlib.pyplot as plt
import contextily as ctx


COLORS = ['#377eb8', '#ff7f00', '#4daf4a',
          '#f781bf', '#a65628', '#984ea3',
          '#999999', '#e41a1c', '#dede00']


def get_random_coordinates(bbox=None, polygon=None):
    """
    Create random start and end points to generate random route requests
    :param
    bbox: list containing xmin, ymin, xmax, ymax of bounding box
    polygon: list of lists containing the coordinates of the polygon
    :return:
    """
    if bbox:
        xmin, ymin, xmax, ymax = bbox
        start_lon = random.uniform(xmin, xmax)
        end_lon = random.uniform(xmin, xmax)
        start_lat = random.uniform(ymin, ymax)
        end_lat = random.uniform(ymin, ymax)
    elif polygon:
        xmin, ymin, xmax, ymax = polygon.bounds
        start_lon = random.uniform(xmin, xmax)
        start_lat = random.uniform(ymin, ymax)
        while not Point(float(start_lon),float(start_lat)).within(polygon):
            start_lon = random.uniform(xmin, xmax)
            start_lat = random.uniform(ymin, ymax)
        end_lat = random.uniform(ymin, ymax)
        end_lon = random.uniform(xmin, xmax)
        while not Point(float(end_lon),float(end_lat)).within(polygon):
            end_lat = random.uniform(ymin, ymax)
            end_lon = random.uniform(xmin, xmax)
    else:
        raise ValueError("Either bbox or polygon must be given.")
    return [[start_lon, start_lat], [end_lon, end_lat]]



def duration_diff(reference, other):
    """calculate difference in duration for fastests routes"""
    return (other.iloc[0].duration - reference.iloc[0].duration) / 60.


def shared_route(geom1, geom2, epsg=32632):
    """
    Calculate share of route 1 that is equal to route 2
    """
    geom2 = geom2.buffer(10)

    diverging_length = geom2.intersection(geom1).length
    total_length_1 = geom1.length
    return 1 - (total_length_1 - diverging_length) / total_length_1


def plot_maps(dfs, titles):
    fig, axes = plt.subplots(2, int(len(dfs) / 2), figsize=(15, 10), tight_layout=True)
    axes = axes.flatten()
    linewidth = 3
    alpha = 0.6
    for i, r in enumerate(dfs):
        r.plot(ax=axes[i - 1], color=COLORS[:len(dfs)], alpha=alpha, linewidth=linewidth)
        axes[i - 1].axis('off')
        ctx.add_basemap(ax=axes[i - 1], source=ctx.providers.Stamen.TonerBackground, zoom=12)

    [ax.set_title(t) for ax, t in zip(axes, titles)]


def find_shared_route(routes_google_df, routes_other_df):
    shared_values = []
    for geom in routes_other_df.geometry:
        shared_values.append(shared_route(routes_google_df.geometry[0], geom))
        return min(shared_values)