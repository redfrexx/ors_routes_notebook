#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""__description__
"""

__author__ = "Christina Ludwig, GIScience Research Group, Heidelberg University"
__email__ = "christina.ludwig@uni-heidelberg.de"

import pytest
from ors_evaluation import Route

BASE_URL = "'https://meingruen.geog.uni-heidelberg.de/ors/'"


def test_extra_info():
    """
    Test wether extra_info is extracted correctly form ors response
    :return:
    """
    params = {'coordinates': [[8.688674220431666, 49.42862241050762], [8.690628006707582, 49.42542725391751]],
                          'profile': "foot-walking",
                          'format': 'geojson',
                          'preference': 'fastest',
                          'instructions': 'false',
                          'extra_info': ['shadow']
                          }

    route = Route(params=params, base_url=BASE_URL)

    route.extras
