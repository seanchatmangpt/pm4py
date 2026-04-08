"""
PM4Py – A Process Mining Library for Python
Copyright (C) 2024 Process Intelligence Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Website: https://processintelligence.solutions
Contact: info@processintelligence.solutions
"""


import importlib.util


def DecisionTreeClassifier(*args, **kwargs):
    from sklearn.tree import DecisionTreeClassifier

    return DecisionTreeClassifier(*args, **kwargs)


def AffinityPropagation(*args, **kwargs):
    from sklearn.cluster import AffinityPropagation

    return AffinityPropagation(*args, **kwargs)


def KMeans(*args, **kwargs):
    from sklearn.cluster import KMeans

    return KMeans(*args, **kwargs)


def KNeighborsRegressor(*args, **kwargs):
    from sklearn.neighbors import KNeighborsRegressor

    return KNeighborsRegressor(*args, **kwargs)


def LocallyLinearEmbedding(*args, **kwargs):
    from sklearn.manifold import LocallyLinearEmbedding

    return LocallyLinearEmbedding(*args, **kwargs)
